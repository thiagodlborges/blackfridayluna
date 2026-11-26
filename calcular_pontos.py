#!/usr/bin/env python3
"""Calcula pontos em dobro da campanha Black Friday (freezer da sede) e gera o Excel por CPF.

Uso: python calcular_pontos.py [data/compras.csv] [saida/pontos_blackfriday.xlsx]

Entrada (CSV com ';' ou ',', inclusive a exportacao da tabela bf_comprovantes do Supabase): cpf;nome;data_compra;valor;id_comprovante
 - data_compra: AAAA-MM-DD ou DD/MM/AAAA
 - valor: aceita 18,50 / 18.50 / 1.234,56
 - id_comprovante: NSU/autorizacao da maquininha (evita pontuar o mesmo comprovante 2x)
"""
import csv
import json
import sys
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

BASE = Path(__file__).parent


def so_digitos(s):
    return "".join(c for c in str(s) if c.isdigit())


def cpf_valido(cpf):
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(cpf[i]) * (n + 1 - i) for i in range(n))
        dv = (soma * 10 % 11) % 10
        if dv != int(cpf[n]):
            return False
    return True


def parse_valor(s):
    s = str(s).strip().replace("R$", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return Decimal(s)


def parse_data(s):
    s = str(s).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError("data invalida")


def fmt_cpf(c):
    return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"


def processar(caminho_csv, config):
    ini = date.fromisoformat(config["periodo_inicio"])
    fim = date.fromisoformat(config["periodo_fim"])
    ppr = Decimal(str(config["pontos_por_real"]))
    aceitas, rejeitadas, vistos = [], [], set()

    with open(caminho_csv, newline="", encoding="utf-8-sig") as f:
        amostra = f.readline()
        f.seek(0)
        delim = ";" if amostra.count(";") >= amostra.count(",") else ","
        for n, linha in enumerate(csv.DictReader(f, delimiter=delim), start=2):
            # exportacao do Supabase usa a coluna "nsu" e traz "status"
            if "id_comprovante" not in linha and "nsu" in linha:
                linha["id_comprovante"] = linha["nsu"]
            def rej(motivo):
                rejeitadas.append({"linha": n, **linha, "motivo": motivo})
            if "status" in linha and (linha["status"] or "").strip().lower() != "aprovado":
                if (linha["status"] or "").strip().lower() == "rejeitado":
                    continue
                rej("Comprovante ainda nao aprovado (status: %s)" % (linha["status"] or "vazio")); continue
            try:
                cpf = so_digitos(linha["cpf"])
                if not cpf_valido(cpf):
                    rej("CPF invalido"); continue
                valor = parse_valor(linha["valor"])
                if valor <= 0:
                    rej("Valor deve ser maior que zero"); continue
                dt = parse_data(linha["data_compra"])
                if not (ini <= dt <= fim):
                    rej(f"Fora do periodo da campanha ({ini:%d/%m/%Y} a {fim:%d/%m/%Y})"); continue
                comp = (linha.get("id_comprovante") or "").strip()
                if not comp:
                    rej("Comprovante sem identificador (NSU)"); continue
                if comp in vistos:
                    rej("Comprovante duplicado"); continue
                vistos.add(comp)
            except (InvalidOperation, ValueError, KeyError) as e:
                rej(f"Linha invalida: {e}"); continue
            aceitas.append({"cpf": cpf, "nome": (linha.get("nome") or "").strip(),
                            "data": dt, "valor": valor, "comprovante": comp})

    por_cpf = OrderedDict()
    for c in aceitas:
        d = por_cpf.setdefault(c["cpf"], {"nome": c["nome"], "compras": 0, "total": Decimal("0")})
        d["compras"] += 1
        d["total"] += c["valor"]
    resumo = []
    for cpf, d in por_cpf.items():
        pontos = int((d["total"] * ppr).to_integral_value(rounding=ROUND_FLOOR))
        resumo.append({"cpf": cpf, "nome": d["nome"], "compras": d["compras"],
                       "total": d["total"], "pontos": pontos})
    return resumo, aceitas, rejeitadas


def gerar_excel(resumo, aceitas, rejeitadas, destino):
    wb = Workbook()
    ws = wb.active
    ws.title = "Pontos"
    ws.append(["CPF", "Nome", "Qtd compras", "Total gasto (R$)", "Pontos a creditar"])
    for r in resumo:
        ws.append([fmt_cpf(r["cpf"]), r["nome"], r["compras"], float(r["total"]), r["pontos"]])
    ws.append([])
    ws.append(["TOTAL", "", sum(r["compras"] for r in resumo),
               float(sum(r["total"] for r in resumo)), sum(r["pontos"] for r in resumo)])
    a = wb.create_sheet("Compras aceitas")
    a.append(["CPF", "Nome", "Data", "Valor (R$)", "Comprovante"])
    for c in aceitas:
        a.append([fmt_cpf(c["cpf"]), c["nome"], c["data"], float(c["valor"]), c["comprovante"]])
    r = wb.create_sheet("Rejeitadas")
    r.append(["Linha no CSV", "CPF", "Nome", "Data", "Valor", "Comprovante", "Motivo"])
    for x in rejeitadas:
        r.append([x["linha"], x.get("cpf"), x.get("nome"), x.get("data_compra"),
                  x.get("valor"), x.get("id_comprovante"), x["motivo"]])
    for sh in wb.worksheets:
        for c in sh[1]:
            c.font = Font(bold=True)
        for col in sh.columns:
            sh.column_dimensions[col[0].column_letter].width = 22
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=4):
        for c in row:
            c.number_format = "#,##0.00"
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)


def main():
    csv_in = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "data" / "compras.csv"
    xlsx_out = Path(sys.argv[2]) if len(sys.argv) > 2 else BASE / "saida" / "pontos_blackfriday.xlsx"
    config = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
    resumo, aceitas, rejeitadas = processar(csv_in, config)
    gerar_excel(resumo, aceitas, rejeitadas, xlsx_out)
    print(f"{len(aceitas)} compras aceitas, {len(rejeitadas)} rejeitadas, "
          f"{len(resumo)} CPFs, {sum(r['pontos'] for r in resumo)} pontos -> {xlsx_out}")


if __name__ == "__main__":
    main()
