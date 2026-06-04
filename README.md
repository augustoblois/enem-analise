# ENEM — Desigualdade Socioeconômica e Desempenho Educacional

**Disciplina:** Análise de Dados · UFPB · 2026  
**Equipe:** Augusto Blois · Pedro Flávio

---

## Problema

O ENEM coleta notas de ~3 milhões de candidatos por edição junto com dados socioeconômicos detalhados (renda, tipo de escola, escolaridade dos pais, região). Apesar da riqueza da base, a magnitude das desigualdades educacionais — e quais fatores mais as explicam — permanece pouco visualizada de forma integrada.

Este projeto quantifica e comunica essas disparidades usando os microdados de 2022 e 2023.

## Público-alvo

Gestores de políticas educacionais (MEC, secretarias estaduais) que precisam de evidências quantitativas para priorizar intervenções. Secundariamente: pesquisadores, equipes pedagógicas e jornalistas de dados.

## Perguntas e Hipóteses

| # | Pergunta | Hipótese inicial |
|---|---|---|
| P1 | Relação entre renda familiar e nota média? | Positiva e monotônica, retornos decrescentes acima de 5 SM |
| P2 | Gap público vs. privado variou entre 2022–2023? | Gap de ~80–120 pts, estável no período |
| P3 | Disparidade regional persiste controlando por renda? | Existe, mas efeito residual < 30 pts após controle |
| P4 | Quais variáveis melhor predizem o desempenho? | Renda + tipo de escola dominam; R² ≥ 0,30 |
| P5 | Perfil dos candidatos com 1000 na Redação? | Escola privada e renda > 3 SM, mas mais diverso que top geral |

## Dados

**Microdados do ENEM** — INEP (público, sem autenticação)  
Edições: 2022 e 2023 · Formato: CSV · Tamanho: ~2–4 GB/edição descompactado

Variáveis principais: `NU_NOTA_*` (5 áreas) · `Q006` (renda) · `TP_ESCOLA` · `SG_UF_PROVA` · `Q001/Q002` (escolaridade dos pais) · `TP_COR_RACA`

## Produto Final

- **Dashboard interativo** (Streamlit) — filtros por ano, UF, renda, tipo de escola; mapa coroplético; correlações
- **Relatório técnico** (PDF) — pipeline, achados, modelo preditivo, conclusões

## Estrutura do Repositório

```
enem-analise/
├── data/          # microdados brutos e processados (não versionados)
├── notebooks/     # análise exploratória e modelagem
├── src/           # scripts de pipeline e dashboard
└── docs/          # entregáveis e documentação
```

## Stack

Python 3.11+ · pandas · matplotlib/seaborn · scikit-learn · Streamlit · Jupyter

## Cronograma

| Semana | Etapa |
|---|---|
| 1 | Extração e verificação dos dados |
| 2 | Limpeza e tratamento |
| 3 | Análise exploratória |
| 4 | Modelagem preditiva |
| 5 | Dashboard e visualizações |
| 6 | Relatório e entrega final |
