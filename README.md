# ENEM — Desigualdade Socioeconômica e Desempenho Educacional

**Disciplina:** Análise de Dados · UFPB · 2026  
**Equipe:** Augusto Blois · Pedro Flávio

> **Status (build em andamento):** governança aprovada (ver `docs/`), construção sprint a sprint via `TASKS.md`. Instruções completas de execução reprodutível na seção [Execução](#execução) abaixo.

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
Edições: 2022 e 2023 (núcleo linkado das 5 perguntas) · Formato: CSV · Tamanho: ~2–4 GB/edição descompactado

Variáveis principais: `NU_NOTA_*` (5 áreas) · `Q006` (renda) · `TP_ESCOLA` · `SG_UF_PROVA` · `Q001/Q002` (escolaridade dos pais) · `TP_COR_RACA`

**Teto temporal: 2023.** A partir de 2024 o INEP separou os microdados em duas bases sem chave comum (`PARTICIPANTES` × `RESULTADOS`, proteção LGPD/ANPD), cortando o pareamento perfil socioeconômico ↔ nota do mesmo indivíduo. Isso é tratado como **achado central de governança de dados** (ver `docs/`): em 2024+ as perguntas P1/P4/P5 (renda/preditores/perfil) deixam de ser respondíveis, enquanto P2 (escola×nota) e P3 (região×nota) **sobrevivem** via `RESULTADOS`.

## Produto Final

- **Dashboard interativo** (Streamlit) — filtros por ano, UF, renda, tipo de escola; mapa coroplético; correlações
- **Relatório técnico** (PDF) — pipeline, achados, modelo preditivo, achado de governança 2024, conclusões e limitações
- **Módulo vivo** — ingestão de edições novas (incl. 2024+) nos eixos que sobrevivem à quebra (escola×nota e região×nota via `RESULTADOS`), sem reprocessar o núcleo socioeconômico 2022–2023

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

## Execução

### 1. Ambiente

Requer Python 3.11+.

```bash
pip install -r requirements.txt
```

### 2. Dados brutos

Os microdados do INEP **não são versionados** (`.gitignore` cobre `data/`, `*.csv`, `*.parquet`) — baixe do INEP e posicione exatamente nestes caminhos (o layout difere por ano):

- 2022 → `data/microdados_enem_2022/DADOS/MICRODADOS_ENEM_2022.csv`
- 2023 → `data/microdados_enem_2023/MICRODADOS_ENEM_2023.csv`

Formato bruto INEP: encoding `latin-1`, separador `;`.

### 3. Pipeline (núcleo 2022+2023)

Execute como **módulo**, a partir da raiz do repo, na ordem abaixo. Todo módulo aceita `--nrows N` para iterar com amostra em vez da base inteira (~1,7 GB) — use sempre para testar antes de rodar a base completa.

```bash
# US-01 — mede memória/tipos das edições brutas via chunking (não grava nada)
python -m src.enem.carga

# US-02 — trata + integra 2022+2023, grava data/processado/enem_2022_2023.parquet
python -m src.enem.tratamento
python -m src.enem.tratamento --nrows 50000   # amostra rápida para validar

# US-04 — EDA: imprime resumo + gera PNGs em docs/figuras/
python -m src.enem.eda

# P1-P5 — perguntas de pesquisa, leem o parquet tratado
python -m src.enem.p1_renda        # P1: renda x nota média
python -m src.enem.p2_escola       # P2: gap pública x privada
python -m src.enem.p3_regiao       # P3: disparidade regional controlando renda
python -m src.enem.p5_redacao1000  # P5: perfil socioeconômico de nota 1000 na redação

# Modelo preditivo (US-09/US-10) — regressão linear interpretável (P4)
python -m src.enem.modelo
```

### 4. Dashboard

```bash
streamlit run src/enem/dashboard.py
```

### 5. Módulo vivo (ingestão de edições novas via RESULTADOS)

A partir de 2024 o INEP separa os microdados em `PARTICIPANTES` × `RESULTADOS` sem chave comum entre si (ver achado de governança em `docs/`). O módulo vivo ingere uma edição nova lendo só o CSV de `RESULTADOS` e recalcula **apenas** os eixos que sobrevivem à quebra — P2 (escola x nota) e P3 (região x nota) — **sem reprocessar o núcleo socioeconômico (SES) 2022+2023**.

```bash
# US-20 — carrega e normaliza uma edição (valida o schema-alvo, não calcula métricas)
python -m src.enem.modulo_vivo --ano 2024
python -m src.enem.modulo_vivo --ano 2024 --nrows 50000

# US-21 — recalcula P2/P3 sobre a edição carregada e imprime saída consolidada
python -m src.enem.modulo_vivo_metricas --ano 2024
```

`--ano` segue o mapeamento de layouts em `modulo_vivo.LAYOUTS`; novas edições exigem adicionar a entrada correspondente nesse mapa, não alterar `carga.py`/`tratamento.py`.
