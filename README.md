# Black Friday — Pontos em Dobro (freezer da sede)

Cada R$ 1,00 gasto no freezer da sede = **2 pontos** no clube da Luna (lunagelato.com.br).

## Fluxo
1. O cliente le o QR code no freezer, abre a pagina (`public/index.html`), informa nome, CPF, data, valor, NSU e anexa a foto do comprovante.
2. O envio vai para o Supabase (tabela `bf_comprovantes` + bucket privado `bf-comprovantes`) com status `pendente`. O publico so consegue **enviar**; nao le, altera nem apaga nada (RLS).
3. No painel do Supabase voce confere a foto (Storage > bf-comprovantes) contra o valor informado e muda o `status` para `aprovado` (ou `rejeitado`).
4. Exporte a tabela `bf_comprovantes` em CSV (Table Editor > Export) e rode `python calcular_pontos.py exportacao.csv`.
5. Suba a aba **Pontos** (CPF + pontos) no programa de fidelidade.

## Publicacao do formulario
Endereco publico (vai no QR code): https://blackfridayluna.vercel.app/

`public/index.html` e uma pagina estatica unica. Publique em Vercel ou Netlify (importando este repositorio privado) e gere o QR code do endereco publico. A chave no HTML e a *publishable* do Supabase: so permite enviar dados, nunca le-los.

## Uso
```bash
pip install -r pontos/requirements.txt
cd pontos && python calcular_pontos.py exportacao.csv
cd pontos && python -m unittest discover -s tests
```

## Formato de `pontos/data/compras.csv` (separador `;`)
`cpf;nome;data_compra;valor;id_comprovante` — data `AAAA-MM-DD` ou `DD/MM/AAAA`; valor `18,50`.

## Regras (em `pontos/config.json`)
- `pontos_por_real`: 2.
- Período: `periodo_inicio` / `periodo_fim`. Compras fora dele são rejeitadas.
- Pontos = piso(total gasto do CPF no período × 2): centavos que não fecham 1 ponto inteiro são descartados uma única vez por CPF, não por compra.
- Linhas com `status` diferente de `aprovado` nao pontuam (`rejeitado` e ignorado; `pendente` aparece na aba Rejeitadas para voce lembrar de conferir).
- Rejeitadas (aba **Rejeitadas**, com o motivo): CPF inválido, valor ≤ 0, fora do período, sem NSU, comprovante duplicado.

## Excel gerado
Abas: **Pontos** (uma linha por CPF, com total), **Compras aceitas** (auditoria), **Rejeitadas**.

> Os dados contêm CPF. Se o repositório for no GitHub, mantenha-o **privado** e não suba `pontos/data/compras.csv` real nem `saida/` (já no `.gitignore`).
