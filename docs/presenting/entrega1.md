# Análise dos Microdados do ENEM: Desigualdade Socioeconômica e Desempenho Educacional no Brasil

**Disciplina:** Análise de Dados  
**Instituição:** Universidade Federal da Paraíba (UFPB)  
**Data:** Junho de 2026

**Equipe:**
- Augusto Blois Almeida Barbosa
- Pedro Flávio Nogueira Ribeiro de Luna

---

## 1. Problema e Justificativa de Relevância

O Exame Nacional do Ensino Médio (ENEM) é o maior exame educacional do Brasil, com mais de 3 milhões de inscritos por edição. Além de ser a principal porta de entrada para o ensino superior via SISU, o exame coleta, por questionário socioeconômico, informações detalhadas sobre o contexto de vida de cada participante: renda familiar, raça/cor, escolaridade dos pais, acesso à internet, tipo de escola, entre outros.

**O problema central:** a educação brasileira reproduz desigualdades estruturais. Candidatos de maior renda, filhos de pais com ensino superior, provenientes de escolas privadas e de regiões mais ricas sistematicamente superam os demais. A magnitude exata dessas diferenças, sua variação ao longo do tempo e os fatores que mais as explicam seguem pouco explorados de forma integrada e visual.

**Justificativa:** os microdados do ENEM combinam indicadores socioeconômicos com notas em cinco áreas de conhecimento, constituindo uma das fontes mais abrangentes para o estudo da desigualdade educacional em escala nacional. O recorte temporal 2022–2023 permite análise comparativa recente.

**O que este projeto entrega:** quantificação, visualização e comunicação dessas disparidades, identificando quais variáveis socioeconômicas exercem maior influência sobre o desempenho, com atenção especial ao contexto nordestino.

---

## 2. Público-alvo e Tomador de Decisão

| Perfil | Uso esperado do produto |
|---|---|
| **Gestores de políticas educacionais** (MEC, secretarias estaduais) | Identificar regiões e perfis que demandam intervenção prioritária |
| **Pesquisadores e docentes de educação** | Base analítica para estudos sobre desigualdade escolar |
| **Equipes pedagógicas de escolas públicas** | Contextualizar desempenho de alunos frente ao perfil socioeconômico |
| **Jornalistas de dados e comunicadores** | Narrativas visuais sobre equidade educacional |

O tomador de decisão primário é o **gestor de política pública educacional**: alguém que precisa de evidências quantitativas para priorizar investimentos e ações afirmativas.

---

## 3. Perguntas Analíticas e Hipóteses Iniciais

**P1 — Renda e desempenho**  
Qual a relação entre faixa de renda familiar e nota média nas cinco áreas?  
*Hipótese:* relação positiva e aproximadamente monotônica, com retornos decrescentes nas faixas mais altas (acima de 5 SM). O efeito da renda deve ser mais pronunciado em Matemática que em Redação.

**P2 — Escola pública vs. privada**  
Qual o gap médio entre candidatos de escolas públicas e privadas? Esse gap variou entre 2022 e 2023?  
*Hipótese:* gap persistente de 80–120 pontos em média. Sem variação significativa entre os dois anos, dado que políticas estruturais não mudam em um ciclo anual.

**P3 — Disparidade regional**  
Candidatos do Nordeste apresentam notas sistematicamente mais baixas que do Sul/Sudeste? A disparidade persiste controlando por renda e tipo de escola?  
*Hipótese:* disparidade regional existe, mas é parcialmente explicada pela composição socioeconômica. Controlando por renda e tipo de escola, o efeito regional residual deve ser menor que 30 pontos.

**P4 — Preditores combinados**  
Quais variáveis socioeconômicas, em conjunto, melhor predizem o desempenho?  
*Hipótese:* renda familiar e tipo de escola serão os dois preditores mais fortes. Escolaridade dos pais contribuirá de forma independente. Um modelo simples (regressão linear) deve capturar R² ≥ 0,30.

**P5 — Perfil da nota 1000 na Redação**  
Qual o perfil socioeconômico dos candidatos com nota máxima na Redação?  
*Hipótese:* concentração em escolas privadas e renda acima de 3 SM, mas com maior diversidade regional que o grupo de alto desempenho geral — a Redação é a área com menor dependência de insumos materiais.

---

## 4. Fontes de Dados e Viabilidade

**Base principal:** Microdados do ENEM — INEP  
**URL:** https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem  
**Edições:** 2022 e 2023  
**Formato:** CSV compactado (.zip), dicionário de variáveis incluso  
**Tamanho estimado:** 2–4 GB por edição (descompactado)  
**Acesso:** público, irrestrito, sem autenticação

**Variáveis de interesse:**

| Variável | Descrição |
|---|---|
| `NU_NOTA_MT`, `NU_NOTA_LC`, `NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_REDACAO` | Notas por área |
| `Q006` | Faixa de renda familiar mensal |
| `Q001`, `Q002` | Escolaridade do pai e da mãe |
| `TP_ESCOLA` | Tipo de escola (pública/privada) |
| `SG_UF_PROVA` | Unidade da Federação |
| `TP_COR_RACA` | Raça/cor autodeclarada |
| `IN_ACESSO_INTERNET` | Acesso à internet em casa |
| `NU_ANO` | Ano da edição |

**Avaliação de viabilidade:** confirmada. Dados amplamente utilizados em pesquisas acadêmicas, com documentação completa e histórico de disponibilidade ininterrupta. Risco de indisponibilidade: nulo.

---

## 5. Produto Final

Dois entregáveis complementares:

**5.1 Dashboard Interativo**  
Desenvolvido em Python com Streamlit. Funcionalidades:
- Filtro por ano, UF, tipo de escola, faixa de renda
- Distribuição de notas por área
- Comparação entre grupos (público vs. privado; Nordeste vs. Sul/Sudeste)
- Mapa coroplético com desempenho médio por estado
- Gráficos de correlação renda × nota

**5.2 Relatório Técnico (PDF)**  
- Pipeline de dados (extração → limpeza → análise → visualização)
- Respostas às cinco perguntas analíticas com gráficos
- Resultados do modelo preditivo (P4) com métricas (R², MAE)
- Conclusões e limitações

---

## 6. Plano de Execução

| Etapa | Atividade | Prazo |
|---|---|---|
| 1. Extração | Download dos microdados 2022 e 2023; verificação de integridade | Semana 1 |
| 2. Tratamento | Limpeza de ausentes; seleção e tipagem de variáveis; amostragem se necessário | Semana 2 |
| 3. EDA | Estatísticas descritivas; distribuições; correlações; comparações entre grupos | Semana 3 |
| 4. Modelagem | Modelo preditivo (P4); métricas R² e MAE | Semana 4 |
| 5. Visualização | Dashboard Streamlit; gráficos do relatório | Semana 5 |
| 6. Entrega | Revisão; relatório técnico; submissão | Semana 6 |

**Stack:** Python 3.11+, pandas, matplotlib/seaborn, scikit-learn, Streamlit, Jupyter Notebook.

---

*Entrega 1 — Projeto Aplicado · Análise de Dados · UFPB · 2026*
