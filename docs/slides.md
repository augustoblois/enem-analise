---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Segoe UI', sans-serif;
    font-size: 22px;
  }
  h1 { color: #1a3a6b; }
  h2 { color: #1a3a6b; border-bottom: 2px solid #1a3a6b; padding-bottom: 4px; }
  table { font-size: 18px; }
  strong { color: #1a3a6b; }
---

# ENEM: Desigualdade Socioeconômica e Desempenho Educacional

**Análise de Dados · UFPB · 2026**

Augusto Blois · Pedro Flávio

---

## O Problema

- ENEM: **~3 milhões** de candidatos/ano + questionário socioeconômico completo
- Base combina **notas em 5 áreas** com renda, tipo de escola, região, escolaridade dos pais
- Desigualdades existem — mas sua **magnitude exata e principais fatores** seguem pouco visualizados

> *Quem são os candidatos que ficam para trás — e por quê?*

---

## Público-alvo

| Perfil | Para que usar |
|---|---|
| Gestores (MEC, secretarias) | Priorizar intervenções com base em evidências |
| Pesquisadores de educação | Base analítica sobre desigualdade escolar |
| Equipes pedagógicas | Contextualizar desempenho de alunos |
| Jornalistas de dados | Narrativas visuais sobre equidade |

**Tomador de decisão primário:** gestor de política pública educacional

---

## Perguntas Analíticas

1. **P1 — Renda:** como a faixa de renda afeta a nota média? A relação é linear?
2. **P2 — Escola:** qual o gap público vs. privado? Mudou entre 2022 e 2023?
3. **P3 — Região:** a disparidade Nordeste vs. Sul/Sudeste persiste após controlar renda?
4. **P4 — Preditores:** quais variáveis socioeconômicas melhor predizem o desempenho?
5. **P5 — Redação 1000:** qual o perfil de quem tirou nota máxima?

---

## Hipóteses Iniciais

| # | Hipótese |
|---|---|
| P1 | Relação positiva e monotônica; retornos decrescentes acima de 5 SM |
| P2 | Gap de ~80–120 pts; estável entre 2022–2023 |
| P3 | Efeito regional residual < 30 pts após controle por renda e escola |
| P4 | Renda + tipo de escola dominam; modelo com R² ≥ 0,30 |
| P5 | Escola privada + renda > 3 SM, mas mais diverso que top geral |

---

## Dados

**Microdados do ENEM — INEP**
- Edições: **2022 e 2023**
- Formato: CSV · ~2–4 GB por edição · Acesso público, sem autenticação

**Variáveis-chave:**
`NU_NOTA_*` · `Q006` (renda) · `TP_ESCOLA` · `SG_UF_PROVA` · `Q001/Q002` (escolaridade dos pais) · `TP_COR_RACA`

Viabilidade: ✅ base estável, documentada, usada amplamente em pesquisa acadêmica

---

## Produto Final

**Dashboard Streamlit**
- Filtros: ano, UF, renda, tipo de escola
- Mapa coroplético por estado
- Gráficos de correlação renda × nota
- Comparação público vs. privado · Nordeste vs. Sul/Sudeste

**Relatório Técnico (PDF)**
- Pipeline completo · Respostas P1–P5 · Modelo preditivo com métricas

---

## Cronograma

| Semana | Etapa |
|---|---|
| 1 | Extração e verificação |
| 2 | Limpeza e tratamento |
| 3 | Análise exploratória |
| 4 | Modelagem preditiva |
| 5 | Dashboard e visualizações |
| 6 | Relatório e entrega final |

**Stack:** Python 3.11+ · pandas · seaborn · scikit-learn · Streamlit · Jupyter

---

## Repositório

```
enem-analise/
├── data/       # microdados brutos e processados
├── notebooks/  # EDA e modelagem
├── src/        # pipeline e dashboard
└── docs/       # entregáveis
```

github.com/augustoblois/enem-analise

---

# Obrigado

**Dúvidas?**

Augusto Blois · Pedro Flávio  
Análise de Dados · UFPB · 2026
