# Black Friday — Pontos em Dobro (freezer da sede)

Cada R$ 1,00 gasto no freezer da sede = **2 pontos** no clube da Luna (lunagelato.com.br).

## Fluxo
1. O colaborador se cadastra no clube, compra no freezer e envia o comprovante da maquininha pelo site.
2. Os dados do comprovante (CPF, nome, data, valor, NSU) são registrados em `data/compras.csv`.
3. `python calcular_pontos.py` valida, soma por CPF e gera `saida/pontos_blackfriday.xlsx`.
4. Você sobe a aba **Pontos** (CPF + pontos a creditar) no programa de fidelidade.

## Uso
```bash
pip install -r requirements.txt
python calcular_pontos.py            # usa data/compras.csv e config.json
python -m unittest discover -s tests
```

## Formato de `data/compras.csv` (separador `;`)
`cpf;nome;data_compra;valor;id_comprovante` — data `AAAA-MM-DD` ou `DD/MM/AAAA`; valor `18,50`.

## Regras (em `config.json`)
- `pontos_por_real`: 2.
- Período: `periodo_inicio` / `periodo_fim`. Compras fora dele são rejeitadas.
- Pontos = piso(total gasto do CPF no período × 2): centavos que não fecham 1 ponto inteiro são descartados uma única vez por CPF, não por compra.
- Rejeitadas (aba **Rejeitadas**, com o motivo): CPF inválido, valor ≤ 0, fora do período, sem NSU, comprovante duplicado.

## Excel gerado
Abas: **Pontos** (uma linha por CPF, com total), **Compras aceitas** (auditoria), **Rejeitadas**.

> Os dados contêm CPF. Se o repositório for no GitHub, mantenha-o **privado** e não suba `data/compras.csv` real nem `saida/` (já no `.gitignore`).
