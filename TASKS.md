# TASKS — Análise dos Microdados do ENEM

> Fonte da verdade viva. Detalhe em docs/backlog.md. Marque [x] ao concluir;
> adicione novas tasks conforme surgirem. Ordenado por prioridade de épico.
> Sprints/datas não pré-atribuídos (P2/P3 SIGAA indefinidos — ver Gaps no backlog).
> **Remodelado em 2026-06-19:** pivot já refletido no PRD (O6, RF-14, EP-02b). O antigo EP-00
> (editar docs de governança) foi concluído — o recorte está no PRD. Adicionado EP-02b (achado 2024);
> US-11 ampliada para incluir a seção do achado 2024 + teto temporal.
> **2ª remodelagem em 2026-06-19:** professor exige produto USÁVEL e vivo. Adicionado **EP-07 (módulo
> vivo, P0)** com US-20..US-23 (ingestão de edição nova nos eixos P2/P3 via RESULTADOS, prova de conceito
> = RESULTADOS 2024 real). **EP-06 (dashboard) repriorizado P1 → P0**; US-15 ganhou task da edição viva;
> US-14 ganhou task de documentar o passo de ingestão. Tudo US-01..US-18 preservado.

## Sprint 1 — Goal: base 2022+2023 tratada, integrada, documentada e reprodutível (roda do zero)
> Roster adaptado (projeto Python DS, não web): construção por `ai-data-engineer` (carga ~1,7 GB) +
> `python-developer`; gate independente por `code-reviewer` (vira o checkbox só se APROVADO).
> designops PULADO (sem shadcn/Tailwind; estética techy do dashboard = `.streamlit/config.toml` na US-15).
> Stories: **US-01, US-02, US-03, US-13**.

## EP-01 — Base analítica: aquisição, tratamento, integração e documentação (P0)
- [x] US-01 — Carga eficiente e tipada dos microdados (3 pts)
  - [x] Listar colunas relevantes a partir do dicionário INEP
  - [x] Definir `dtype` por coluna (categóricas como `category`, notas como `float`)
  - [x] Leitura com `usecols` + `dtype`; medir uso de memória
  - [x] Chunking/amostragem documentada se não couber
  - [x] Validar contagem de linhas e tipos
- [x] US-02 — Tratamento e integração 2022+2023 com marcador de ano (5 pts) — depende de US-01
  - [x] Mapear correspondência de variáveis 2022 vs. 2023 (validar comparabilidade)
  - [x] Regra de tratamento de nulos por variável (documentar)
  - [x] Recodificar Q006 (renda), Q001/Q002 (escolaridade pais), tipo de escola
  - [x] Concatenar 2022+2023 com coluna `ano`
  - [x] Persistir base tratada em formato eficiente (parquet), fora do versionamento
  - [x] Validar consistência (categorias, faixas, contagem por ano)
- [x] US-03 — Dicionário e decisões da base analítica (1 pt) [ÂNCORA] — depende de US-02
  - [x] Tabelar variáveis: código original → nome legível → tipo → categorias
  - [x] Registrar regra de nulos e recodificações com justificativa
  - [x] Revisar com a dupla

## EP-02 — EDA e respostas às perguntas analíticas P1–P5 (P0)
- [x] US-04 — EDA inicial da base (3 pts) — depende de US-02
  - [x] Distribuições das notas por área e da redação
  - [x] Resumo descritivo das variáveis socioeconômicas
  - [x] Pelo menos uma comparação de grupos exploratória
  - [x] Anotar observações (outliers, assimetria, nulos residuais)
- [x] US-05 — P1: renda × nota média nas 5 áreas (3 pts) — depende de US-04
  - [x] Agrupar por faixa de renda e calcular média por área + geral
  - [x] Estatística de suporte (gap topo×base ou correlação)
  - [x] Visualização legível
  - [x] Conclusão de P1
- [x] US-06 — P2: gap escola pública vs. privada e variação 2022→2023 (3 pts) — depende de US-04
  - [x] Média por tipo de escola por ano
  - [x] Gap por ano e variação 2022→2023
  - [x] Visualização comparativa
  - [x] Conclusão de P2
- [x] US-07 — P3: disparidade regional controlando renda e tipo de escola (5 pts) — depende de US-04
  - [x] Diferença bruta Nordeste vs. Sul/Sudeste
  - [x] Estratificar/controlar por renda e tipo de escola
  - [x] Visualização da disparidade controlada
  - [x] Conclusão de P3 com ressalva de não-causalidade
- [x] US-08 — P5: perfil socioeconômico das notas 1000 na Redação (3 pts) — depende de US-04
  - [x] Filtrar candidatos com 1000 na redação
  - [x] Perfil por renda/escola/região/escolaridade dos pais
  - [x] Comparar com distribuição geral
  - [x] Visualização e conclusão de P5

## EP-02b — Achado de governança 2024: quebra do linkage SES↔nota (P0 · serve O6)
> Não ingere dados SES de 2024 — documenta a inviabilidade. Independente do pipeline 2022–2023.
> (Os eixos que SOBREVIVEM — escola/região×nota via RESULTADOS — são ingeridos no EP-07, não aqui.)
- [x] US-17 — Documentar a quebra de linkage 2024 (correção factual) (3 pts) — depende de —
  - [x] Ler `Leia_Me_Enem_2024.pdf` (INEP, jun/2025): localizar as duas bases e a chave
  - [x] Redigir descrição factual: PARTICIPANTES vs. RESULTADOS, ausência de chave comum
  - [x] Registrar base legal (LGPD/ANPD) com tom factual, citando a fonte
  - [ ] Revisão cruzada da dupla conferindo cada afirmação contra o documento
- [x] US-18 — Mapear perguntas que morrem vs. sobrevivem em 2024+ e fixar teto temporal (2 pts) — depende de US-17
  - [x] Classificar P1–P5 + raça×nota + sexo×nota como "morre" ou "sobrevive" em 2024+, com a razão
  - [x] Justificar por escrito o teto temporal 2023 como consequência da quebra
  - [x] Conectar o mapeamento à seção de limitações do relatório (insumo para US-11) e ao escopo do módulo vivo (EP-07)

## EP-03 — Modelagem preditiva interpretável (P4) (P0)
- [x] US-09 — Fechar definição do alvo e variáveis do modelo P4 (2 pts) — depende de US-03
  - [x] Avaliar prós/contras alvo = nota média vs. nota por área
  - [x] Decidir o alvo com a dupla e registrar justificativa
  - [x] Listar variáveis preditoras (`X`) com justificativa
- [x] US-10 — Treinar e avaliar a regressão linear (R²/MAE + ranking) (5 pts) — depende de US-09
  - [x] Preparar `X`/`y` (encoding, split treino/teste com `random_state`)
  - [x] Treinar regressão linear
  - [x] Reportar R² e MAE no teste
  - [x] Ranking de variáveis por contribuição
  - [x] Conclusão de P4 com limitação do R² baixo

## EP-04 — Comunicação executiva: relatório técnico e síntese (P0 · marco P3, peso 40%)
- [x] US-11 — Relatório técnico em PDF (inclui achado 2024 + teto temporal) (8 pts) — depende de US-05, US-06, US-07, US-08, US-10, US-18
  - [x] Estruturar relatório (pipeline → P1–P5 → modelo → achado de governança 2024 → conclusões → limitações)
  - [x] Inserir gráficos finais e estatísticas
  - [x] Redigir a seção do achado 2024 (de US-17/US-18): duas bases, LGPD/ANPD, perguntas mortas vs. vivas, teto 2023
  - [x] Redigir conclusões e limitações (R² baixo, não-causalidade, teto temporal 2023)
  - [ ] Exportar PDF e revisar com a dupla (conferir seção 2024 contra a fonte primária)
- [ ] US-12 — Síntese executiva (2 pts) — depende de US-11
  - [ ] Destilar achados-chave de P1–P5, do modelo e do achado de governança 2024
  - [ ] Escrever problema → evidências → implicações → limitações → recomendações
  - [ ] Revisar tom executivo com a dupla

## EP-05 — Reprodutibilidade do repositório (P0 · critério explícito de P3)
- [x] US-13 — Ambiente fixado e dados fora do versionamento (2 pts) — depende de US-01
  - [x] Fixar dependências com versões
  - [x] `.gitignore` cobrindo `data/` e artefatos intermediários
  - [x] Verificar que nenhum dado está versionado no histórico
- [x] US-14 — README com ordem de execução reprodutível (3 pts) — depende de US-11, US-13
  - [x] Documentar instalação do ambiente e onde colocar os dados
  - [x] Documentar a ordem de execução do pipeline
  - [x] Documentar o passo de ingestão do módulo vivo (rodar a rotina com um novo CSV RESULTADOS)
  - [x] Testar o passo a passo em ambiente limpo (revisão cruzada)

## EP-06 — Dashboard interativo Streamlit (P0)
> Repriorizado P1 → P0 na 2ª remodelagem — face usável exigida pelo professor.
- [x] US-15 — Dashboard Streamlit com filtros que atualizam visualizações (5 pts) — depende de US-04
  - [x] Configurar `.streamlit/config.toml` (dark theme, primaryColor neon, font mono) — estética techy RNF-05
  - [x] Carregar base tratada de forma eficiente (cache)
  - [x] Filtros: ano, UF, tipo de escola, faixa de renda
  - [x] ≥4 visualizações reativas em Plotly (`plotly_dark`)
  - [x] KPI cards (`st.metric`) no topo + layout em grid (`st.tabs`/`st.columns`)
  - [ ] Validar que cada filtro atualiza as visualizações
  - [x] Garantir que o filtro de ano comporta a(s) edição(ões) viva(s) de P2/P3 sem afetar as visões SES
- [x] US-16 — Mapa coroplético por estado e correlação renda×nota (5 pts) — depende de US-15
  - [x] Obter/usar malha de UF do Brasil (GeoJSON de estados)
  - [x] Renderizar coroplético por estado com Plotly (`px.choropleth`, `plotly_dark`) reagindo aos filtros
  - [x] Visualização e estatística de correlação renda×nota (Plotly)
  - [ ] Validar consistência mapa/correlação com filtros
> US-19 (em aberto, NÃO semeada): visualização do achado 2024 no dashboard. Só entra se o PM/dupla
> aprovar no gate → dependeria de US-15. Ver "⚠️ Gaps para o PM" no backlog.

## EP-07 — Módulo vivo: ingestão de edições novas nos eixos que sobrevivem à quebra (P2/P3) (P0 · serve O7)
> Só escola×nota (P2) e região×nota (P3) via RESULTADOS. NÃO reprocessa o núcleo SES (RNF-07).
> MVP = ingestão manual. Layout difere por edição (2024 = dois CSVs em `DADOS/`; 2023 = CSV único; 2022 = próprio).
> Prova de conceito = RESULTADOS 2024 real (já baixado).
- [x] US-20 — Carregador de edição parametrizável por ano (abstrai o layout que difere) (5 pts) — depende de —
  - [x] Mapeamento de layout por edição (qual é o RESULTADOS, onde fica, encoding/separador)
  - [x] Leitura parametrizada por ano com `usecols`/`dtype` (eficiente — RNF-02)
  - [x] Normalizar para schema-alvo: escola/tipo de escola, UF/região, notas, `ano` (nomes padronizados)
  - [x] Detectar e tratar divergência de headers/codificação de escola como passo explícito (não silenciar)
  - [x] Validar isolamento do núcleo SES (entrada própria, sem import do pipeline 2022–2023)
- [x] US-21 — Recálculo de P2/P3 sobre a edição ingerida (5 pts) — depende de US-20
  - [x] Calcular P2 (média e gap pública×privada) sobre o DataFrame normalizado, por `ano`
  - [x] Calcular P3 (disparidade região×nota) sobre o DataFrame normalizado, por `ano`
  - [x] Consolidar/empilhar métricas por `ano` (saída comparável entre edições)
  - [x] Garantir reprodutibilidade e isolamento do núcleo SES
- [x] US-22 — Atualizar as saídas (dashboard/relatório) com a edição viva ingerida (3 pts) — depende de US-21, US-15
  - [x] Ligar a saída consolidada de P2/P3 por `ano` (US-21) às visões do dashboard
  - [x] Garantir que a edição viva entra no filtro de ano sem contaminar as visões SES
  - [x] (Se o relatório exibir P2/P3 por edição) prever ponto de inserção das métricas vivas
  - [x] Validar que ingerir uma edição nova atualiza as saídas só rodando a rotina (sem editar código)
- [x] US-23 — Prova de conceito: ingerir RESULTADOS 2024 e exibir P2/P3 lado a lado com 2022–2023 (3 pts) — depende de US-22
  - [x] Apontar o carregador para 2024 (RESULTADOS_2024.csv real, layout de dois CSVs em `DADOS/`)
  - [x] Validar headers/codificação reais de 2024 vs. 2022–2023; documentar divergências e o alinhamento
  - [x] Rodar US-20→US-21→US-22 ponta a ponta para 2024
  - [x] Conferir P2/P3 de 2024 exibidos ao lado de 2022–2023 e registrar a evidência
  - [x] Confirmar e registrar que o núcleo SES não foi reprocessado
