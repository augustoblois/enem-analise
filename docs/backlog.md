# Backlog — Análise dos Microdados do ENEM (Desigualdade Socioeconômica × Desempenho)

> Fonte: docs/prd.md (aprovado). Gerado pelo scrum-master.
> Projeto acadêmico de Data Science (UFPB / PSAE00263 - T01). NÃO é web-app:
> as "fatias verticais" aqui são fatias de pipeline de dados / análise, não de UI web.
> Stack: Python 3.11+, pandas, numpy, scikit-learn, Streamlit, Jupyter, relatório PDF. Gráficos: **Plotly no dashboard** (`plotly_dark`, interativo); **matplotlib/seaborn restritos ao relatório PDF**. Dashboard segue estética techy/dark (RNF-05).
> Equipe: dupla (Augusto + Pedro). Dados já baixados em `data/microdados_enem_2022/`, `2023/` e `2024/`.
> **Núcleo analítico das 5 perguntas (P1–P5) = edições linkadas 2022–2023** (questionário + nota na
> mesma linha). A janela **2009–2023** é só o enquadramento textual da tese (janela viável/defensável);
> NÃO é a base de aquisição — nenhuma story ingere as 14 edições. O teto temporal do **núcleo SES** é
> **2023**: a partir de 2024 o INEP quebrou o linkage SES↔nota (LGPD/ANPD), o que vira **achado central
> de governança** (EP-02b), não nota de rodapé.
> **Remodelado em 2026-06-19** após o pivot do PRD (O6, RF-14, EP-02b). Stories US-01..US-16 preservadas;
> adicionadas US-17/US-18 (EP-02b) e US-11 ampliada para cobrir a seção do achado 2024 + teto temporal.
> **2ª remodelagem em 2026-06-19** — o professor exige um **produto USÁVEL e vivo**. Adicionado **EP-07
> (módulo vivo, P0)** com US-20..US-23: ingerir edições novas (incl. 2024) **só** nos eixos que sobrevivem
> à quebra — escola×nota (P2) e região×nota (P3) via RESULTADOS — **sem reprocessar o núcleo SES 2022–2023**.
> Prova de conceito = ingestão de **RESULTADOS 2024 real** (já baixado). **EP-06 (dashboard) repriorizado
> P1 → P0** (face usável exigida): US-15/US-16 agora P0; US-15 ganha task de exibir a edição viva ingerida.
> Tudo US-01..US-18 preservado.

## Definition of Done (todas as stories — barra universal pro checkbox)
- [ ] Critérios de aceite (Given/When/Then) atendidos e demonstráveis (gráfico/tabela/número defensável).
- [ ] Código roda **do zero** sem erro (ambiente limpo) e na ordem de execução documentada.
- [ ] Reprodutível: mesmo input → mesmo output; `random_state`/seeds fixados onde houver aleatoriedade.
- [ ] Documentado: cada decisão de tratamento/recodificação/análise registrada; a dupla consegue defender cada trecho (RNF-03).
- [ ] Revisado pela dupla (quem escreve não vira o próprio checkbox — o outro membro revisa).
- [ ] Nenhum dado bruto/intermediário versionado (`.gitignore` cobre `data/`) — RNF-04.
- [ ] Performance OK: roda em máquina comum sem estourar memória (tipagem, seleção de colunas, amostragem documentada) — RNF-02.
- [ ] Tudo em pt-BR; identificadores de código e termos técnicos exatos (RNF-06).
- [ ] Visualizações legíveis (eixos rotulados, legenda, escala honesta) — RNF-05, quando a story gera gráfico.
- [ ] Afirmações factuais sobre governança de dados (achado 2024) conferidas contra fonte primária (`Leia_Me_Enem_2024.pdf`) — RNF-04, quando a story toca o achado.
- [ ] Módulo vivo desacoplado: stories de EP-07 **não** reprocessam nem alteram o pipeline do núcleo SES 2022–2023; o ponto de entrada da nova edição é isolado e documentado para o avaliador repetir (RNF-07, RNF-03).

## Definition of Ready (entrada no TASKS.md)
Uma story só é semeada quando tem: aceite Given/When/Then · dependências identificadas ·
regras de negócio/análise claras · estimativa em pontos · trace ao RF + epic.
Faltou algum → afia a story ou registra em "⚠️ Gaps para o PM"; não semeia incompleta.

## Âncora de estimativa
**US-03 (documentar a base = dicionário das variáveis usadas) = 1 ponto** — a story mais simples,
puro registro de decisões já tomadas. Todas as outras são relativas a ela.
Lembrete: pontos medem complexidade + incerteza + esforço, NÃO horas. ≥13 = épico disfarçado → fatiar.

## ⚠️ Gaps para o PM
- **Datas oficiais de P2 e P3 (SIGAA) seguem indefinidas** — o PRD já registra isso. Backlog
  ordenado por **prioridade de épico (P0)**, NÃO por data. Não bloqueia o fatiamento,
  mas bloqueia transformar épicos em sprints com ordem temporal real. Confirmar antes do `/app-build`.
- **Cadência da ingestão do módulo vivo (manual vs. automatizada) está "A definir"** — o PRD assume
  **MVP = ingestão manual de um CSV RESULTADOS de nova edição**, com 2024 como prova de conceito.
  EP-07 foi fatiado nessa premissa (rotina manual, sem pull do INEP / agendamento). Se o professor
  espera automação, EP-07 amplia de escopo — confirmar no gate.
- **Compatibilidade dos headers de RESULTADOS 2024 com 2022–2023 NÃO foi confirmada** — o carregador
  parametrizável (US-20) assume que escola+nota coabitam em RESULTADOS e que a codificação de escola/UF
  é alinhável. Se a validação dos headers na fase de build mostrar divergência, US-20 vira reconciliação
  de schema (pode subir de estimativa). Risco residual: edição futura pode remover escola de RESULTADOS,
  encerrando o módulo vivo — documentar a dependência. **Verificar na fase de build, não bloqueia o fatiamento.**
- A **definição do alvo do modelo P4** (nota média vs. nota por área) NÃO é gap bloqueante: foi
  transformada na story **US-09**, que fecha a decisão cedo dentro de EP-03. Resolvida no backlog.
- **Visualização do achado 2024 no dashboard** (ex.: linha do tempo janela linkada × teto 2024) ficou
  **em aberto** no briefing e como Premissa no PRD ("se decidido, no dashboard"). EP-02b foi fatiado
  **só com cobertura no relatório** (US-17, US-18 → US-11). A story de visualização no dashboard NÃO
  foi semeada — é decisão do PM/dupla no gate. Se aprovada, vira US-19 dependente de US-15.

---

## EP-01 — Base analítica: aquisição, tratamento, integração e documentação (P0 · serve O2 · marco P2)
> Intento (PM): permitir que o pesquisador parta de uma base ENEM 2022–2023 limpa, integrada e
> documentada, sem reprocessar CSVs brutos de 1,7 GB a cada análise. Cobre RF-01, RF-02, RF-03.

### US-01 — Carga eficiente e tipada dos microdados · 3 pts · depende de: — · trace: RF-01, RNF-02
**Como** pesquisador, **quero** carregar os CSVs brutos de 2022 e 2023 com seleção de colunas e tipagem,
**para** trabalhar a base sem estourar a memória da máquina.

**Critérios de aceite**
- **Dado** o CSV bruto de ~1,7 GB de uma edição, **quando** rodar o script de carga com lista de colunas
  relevantes e `dtype` definido, **então** a base carregada contém apenas as colunas selecionadas, tipadas, e cabe em memória.
- **Dado** que a máquina é comum, **quando** a carga rodar, **então** não estoura memória (uso de
  `usecols`/`dtype` e, se necessário, chunking ou amostragem **documentada**).
- **Dado** o script de carga, **quando** rodado do zero, **então** reproduz a mesma base (mesmo input → mesmo output).

**Tasks**
- [ ] Listar as colunas relevantes (nota por área, redação, Q006/Q001/Q002, UF, tipo de escola, ano) a partir do dicionário INEP.
- [ ] Definir o `dtype` de cada coluna (categóricas como `category`, notas como `float`).
- [ ] Implementar leitura com `usecols` + `dtype`; medir uso de memória.
- [ ] Se não couber: aplicar chunking ou amostragem e **documentar** o critério/tamanho da amostra.
- [ ] Validar contagem de linhas e tipos resultantes.

### US-02 — Tratamento e integração 2022+2023 com marcador de ano · 5 pts · depende de: US-01 · trace: RF-02
**Como** pesquisador, **quero** tratar nulos/tipos, recodificar variáveis socioeconômicas e unificar
2022+2023 com uma coluna de ano, **para** ter uma base analítica única e comparável entre edições.

**Critérios de aceite**
- **Dado** as bases carregadas das duas edições, **quando** rodar o tratamento, **então** nulos e tipos
  estão tratados segundo regra documentada e a base final tem uma coluna `ano` (2022/2023).
- **Dado** as variáveis socioeconômicas (renda Q006, escolaridade dos pais Q001/Q002, tipo de escola),
  **quando** recodificadas, **então** seguem categorias legíveis e estáveis entre as duas edições.
- **Dado** o risco de comparabilidade entre edições, **quando** unificar, **então** as diferenças de
  questionário/codificação 2022 vs. 2023 foram validadas e o tratamento de divergências está documentado.

**Tasks**
- [ ] Mapear correspondência de variáveis 2022 vs. 2023 (validar comparabilidade antes de unificar).
- [ ] Definir e aplicar regra de tratamento de nulos por variável (documentar).
- [ ] Recodificar Q006 (faixas de renda), Q001/Q002 (escolaridade dos pais), tipo de escola.
- [ ] Concatenar 2022+2023 adicionando coluna `ano`.
- [ ] Persistir a base analítica tratada em formato eficiente (ex.: parquet) — fora do versionamento.
- [ ] Validar consistência (categorias, faixas, contagem por ano).

### US-03 — Dicionário e decisões da base analítica · 1 pt · depende de: US-02 · trace: RF-03, RNF-03 · [ÂNCORA]
**Como** pesquisador, **quero** um dicionário das variáveis usadas e o registro das decisões de tratamento,
**para** que qualquer avaliador (e a dupla) entenda e defenda a base.

**Critérios de aceite**
- **Dado** a base analítica tratada, **quando** abrir o dicionário, **então** cada variável usada tem nome,
  origem (código INEP), tipo, categorias/recodificação e significado em pt-BR.
- **Dado** as decisões de nulos/tipos/recodificação tomadas em US-02, **quando** lidas no doc, **então**
  cada decisão tem justificativa registrada.

**Tasks**
- [ ] Tabelar variáveis usadas: código original → nome legível → tipo → categorias.
- [ ] Registrar regra de tratamento de nulos e recodificações com justificativa.
- [ ] Revisar com a dupla para garantir que ambos defendem cada decisão.

---

## EP-02 — EDA e respostas às perguntas analíticas P1–P5 (P0 · serve O1)
> Intento (PM): cada uma das 5 perguntas respondida com número e gráfico, mostrando magnitude e
> tendência da desigualdade no **núcleo linkado 2022–2023**. Cobre RF-04, RF-05, RF-06, RF-07, RF-09.
> (P4 não está aqui — é o EP-03, modelagem.)

### US-04 — EDA inicial da base · 3 pts · depende de: US-02 · trace: RF-04, O2
**Como** pesquisador, **quero** uma EDA inicial (distribuições de nota, perfis socioeconômicos, comparações de grupo),
**para** entender a base e fundamentar as respostas P1–P5.

**Critérios de aceite**
- **Dado** a base tratada, **quando** rodar a EDA, **então** existem distribuições das notas (5 áreas + redação),
  resumos dos perfis socioeconômicos e ao menos uma comparação de grupos, cada um com gráfico legível.
- **Dado** a EDA, **quando** revisada, **então** observações iniciais (outliers, assimetrias, nulos residuais) estão anotadas.

**Tasks**
- [ ] Distribuições das notas por área e da redação (histograma/boxplot).
- [ ] Resumo descritivo das variáveis socioeconômicas (frequências por faixa de renda/escola/região).
- [ ] Pelo menos uma comparação de grupos exploratória.
- [ ] Anotar observações (outliers, assimetria, nulos residuais).

### US-05 — P1: renda × nota média nas 5 áreas · 3 pts · depende de: US-04 · trace: RF-05, O1
**Como** gestor, **quero** ver a relação entre faixa de renda familiar e a nota média nas 5 áreas,
**para** dimensionar quanto a renda separa o desempenho.

**Critérios de aceite**
- **Dado** a base tratada, **quando** agrupar por faixa de renda (Q006), **então** existe a nota média
  por área (e geral) por faixa, com gráfico legível e uma estatística de suporte (gap/correlação).
- **Dado** o resultado, **quando** lido, **então** há uma conclusão escrita em pt-BR respondendo P1.

**Tasks**
- [ ] Agrupar por faixa de renda e calcular média por área + geral.
- [ ] Calcular estatística de suporte (gap topo×base ou correlação faixa×nota).
- [ ] Gerar visualização legível.
- [ ] Escrever conclusão de P1.

### US-06 — P2: gap escola pública vs. privada e variação 2022→2023 · 3 pts · depende de: US-04 · trace: RF-06, O1
**Como** gestor, **quero** o gap de desempenho entre escola pública e privada e como ele variou de 2022 para 2023,
**para** saber se a desigualdade por tipo de escola está aumentando ou diminuindo.

**Critérios de aceite**
- **Dado** a base com coluna `ano`, **quando** comparar pública vs. privada por ano, **então** existe o
  gap (diferença de média) para 2022 e 2023 e a variação entre eles, com gráfico e estatística de suporte.
- **Dado** o resultado, **quando** lido, **então** há conclusão escrita respondendo P2 (gap e tendência).

**Tasks**
- [ ] Calcular média por tipo de escola por ano.
- [ ] Calcular gap por ano e a variação 2022→2023.
- [ ] Visualização comparativa (barras agrupadas por ano).
- [ ] Escrever conclusão de P2.

### US-07 — P3: disparidade regional controlando renda e tipo de escola · 5 pts · depende de: US-04 · trace: RF-07, O1
**Como** gestor, **quero** a disparidade Nordeste vs. Sul/Sudeste e se ela persiste ao controlar renda e tipo de escola,
**para** saber se a diferença regional é "própria" da região ou explicada por composição socioeconômica.

**Critérios de aceite**
- **Dado** a base, **quando** comparar as macrorregiões, **então** existe a diferença bruta de nota com gráfico.
- **Dado** controles simples (renda, tipo de escola), **quando** comparar grupos comparáveis, **então**
  mostra-se se o gap regional persiste após o controle, com estatística de suporte.
- **Dado** o escopo (sem causalidade), **quando** concluir, **então** a conclusão escrita evita afirmação causal
  e responde P3.

**Tasks**
- [ ] Calcular diferença bruta de nota Nordeste vs. Sul/Sudeste.
- [ ] Estratificar/controlar por faixa de renda e tipo de escola (comparação simples, sem causalidade).
- [ ] Visualização da disparidade controlada.
- [ ] Escrever conclusão de P3 com ressalva de não-causalidade.

### US-08 — P5: perfil socioeconômico das notas 1000 na Redação · 3 pts · depende de: US-04 · trace: RF-09, O1
**Como** gestor, **quero** o perfil socioeconômico dos candidatos que tiraram 1000 na Redação,
**para** entender quem alcança o topo absoluto e quão concentrado ele é.

**Critérios de aceite**
- **Dado** a base, **quando** filtrar nota 1000 na Redação, **então** existe o perfil desse grupo
  (distribuição por renda, escola, região, escolaridade dos pais) com gráfico legível.
- **Dado** o perfil, **quando** comparado ao perfil geral, **então** a conclusão escrita responde P5
  destacando a concentração (ou não) por estrato.

**Tasks**
- [ ] Filtrar candidatos com 1000 na redação.
- [ ] Descrever perfil por renda/escola/região/escolaridade dos pais.
- [ ] Comparar com a distribuição geral.
- [ ] Visualização e conclusão de P5.

---

## EP-02b — Achado de governança 2024: quebra do linkage SES↔nota (P0 · serve O6)
> Intento (PM): permitir que o gestor e o pesquisador entendam, com correção factual, por que a análise
> SES×desempenho para em 2023 — as duas bases 2024 sem chave comum (LGPD/ANPD), quais perguntas deixam
> de ser respondíveis (P1/P4/P5 + raça×nota + sexo×nota) e quais sobrevivem (P2/P3 via RESULTADOS) —
> transformando a limitação em contribuição (rigor + utilidade). Cobre RF-14.
> Núcleo 2022–2023 NÃO é afetado: a quebra é um fato de 2024+. Estas stories NÃO ingerem dados de 2024 —
> a análise SES×nota de 2024+ está fora de escopo; aqui se **documenta a inviabilidade**, não se analisa.
> (A ingestão dos eixos que SOBREVIVEM — escola/região×nota via RESULTADOS — é EP-07, não aqui.)

### US-17 — Documentar a quebra de linkage 2024 (correção factual) · 3 pts · depende de: — · trace: RF-14, O6
**Como** pesquisador, **quero** descrever com correção factual como o INEP separou os microdados 2024 em
duas bases sem chave comum, **para** fixar o achado de governança que justifica o teto temporal 2023.
> Independente do pipeline 2022–2023 (não depende de US-01..US-04); só depende de ler a fonte primária.

**Critérios de aceite**
- **Dado** o `Leia_Me_Enem_2024.pdf` (INEP, jun/2025) como fonte primária, **quando** redigir a descrição,
  **então** ela define as duas bases — PARTICIPANTES (questionário/renda/demografia, sem nota/escola) e
  RESULTADOS (escola/notas, sem questionário/demografia) — e afirma que **não há chave comum** para parear
  SES↔nota do mesmo indivíduo.
- **Dado** a base legal, **quando** citada, **então** o texto menciona a proteção LGPD validada pela ANPD,
  com correção factual (sem julgamento), e referencia a fonte documental.
- **Dado** o achado, **quando** revisado, **então** cada afirmação factual foi conferida diretamente contra
  o `Leia_Me_Enem_2024.pdf` (não de memória) — RNF-04.

**Tasks**
- [ ] Ler `Leia_Me_Enem_2024.pdf` (INEP, jun/2025) e localizar a descrição das duas bases e da chave.
- [ ] Redigir a descrição factual: PARTICIPANTES vs. RESULTADOS, ausência de chave comum.
- [ ] Registrar a base legal (LGPD/ANPD) com tom factual, citando a fonte.
- [ ] Revisão cruzada da dupla conferindo cada afirmação contra o documento.

### US-18 — Mapear quais perguntas morrem vs. sobrevivem em 2024+ e fixar o teto temporal · 2 pts · depende de: US-17 · trace: RF-14, O6
**Como** gestor, **quero** saber, do conjunto P1–P5 (+ raça×nota, sexo×nota), o que deixa de ser respondível
a partir de 2024 e o que sobrevive, **para** entender o alcance exato da limitação e por que a tese para em 2023.
> Independente do pipeline analítico 2022–2023; é trabalho de mapeamento conceitual, não de dados.

**Critérios de aceite**
- **Dado** a descrição da quebra (US-17), **quando** mapear as perguntas, **então** fica explícito que
  **morrem em 2024+**: P1, P4, P5 + raça×nota + sexo×nota (dependem de SES↔nota no mesmo indivíduo); e
  **sobrevivem via RESULTADOS**: P2 e P3 (escola×nota, região×nota — não precisam do questionário).
- **Dado** o mapeamento, **quando** concluído, **então** o teto temporal **2023** está justificado por escrito
  como decorrência direta da quebra (não como escolha arbitrária).
- **Dado** o escopo, **quando** redigido, **então** o texto deixa claro que 2024+ entra **só como limitação
  documentada** no núcleo SES, nunca como dado SES analisado (alinhado ao "Fora de escopo" do PRD); os eixos
  que sobrevivem (P2/P3) são, esses sim, ingeridos pelo módulo vivo (EP-07).

**Tasks**
- [ ] Classificar cada pergunta (P1–P5 + raça×nota + sexo×nota) como "morre" ou "sobrevive" em 2024+, com a razão.
- [ ] Justificar por escrito o teto temporal 2023 como consequência da quebra.
- [ ] Conectar o mapeamento à seção de limitações do relatório (insumo para US-11) e ao escopo do módulo vivo (EP-07).

---

## EP-03 — Modelagem preditiva interpretável (P4) (P0 · serve O3, O1)
> Intento (PM): mostrar quais fatores socioeconômicos combinados mais predizem desempenho, com erro
> (MAE/R²) e ranking de variáveis explícitos. Cobre RF-08. Apenas regressão linear (escopo).

### US-09 — Fechar a definição do alvo e variáveis do modelo P4 · 2 pts · depende de: US-03 · trace: RF-08, O3
**Como** pesquisador, **quero** decidir e documentar cedo o alvo do modelo (nota média das áreas vs. nota por área)
e o conjunto de variáveis socioeconômicas preditoras, **para** destravar a modelagem sem retrabalho.
> Fecha a Premissa em aberto do PRD (alvo P4). É decisão da dupla, registrada por escrito.

**Critérios de aceite**
- **Dado** a base e o dicionário, **quando** a dupla decidir, **então** o alvo (`y`) está definido e justificado
  por escrito (nota média OU nota de uma área específica).
- **Dado** a decisão, **quando** registrada, **então** o conjunto de variáveis preditoras (`X`) socioeconômicas
  está listado com justificativa, pronto para US-10.

**Tasks**
- [ ] Avaliar prós/contras de alvo = nota média vs. nota por área.
- [ ] Decidir o alvo com a dupla e registrar a justificativa.
- [ ] Listar as variáveis preditoras socioeconômicas (`X`) com justificativa.

### US-10 — Treinar e avaliar a regressão linear (R²/MAE + ranking) · 5 pts · depende de: US-09 · trace: RF-08, O3, O1
**Como** gestor, **quero** um modelo de regressão linear que prevê o desempenho a partir das variáveis socioeconômicas,
com R²/MAE e ranking de variáveis, **para** ver quais fatores combinados mais pesam.

**Critérios de aceite**
- **Dado** o alvo e as variáveis de US-09, **quando** treinar a regressão linear com split treino/teste e seed fixa,
  **então** R² e MAE são reportados **no conjunto de teste** (referência R²≈0,30 do entrega1.pdf).
- **Dado** o modelo treinado, **quando** inspecionado, **então** existe um ranking das variáveis por contribuição.
- **Dado** o R² esperado baixo, **quando** concluir, **então** o resultado é comunicado como **limitação legítima**,
  não como falha, respondendo P4.
- **Dado** a seed fixa e o pipeline, **quando** rodado do zero, **então** reproduz as mesmas métricas.

**Tasks**
- [ ] Preparar `X`/`y` (encoding das categóricas, split treino/teste com `random_state`).
- [ ] Treinar a regressão linear.
- [ ] Reportar R² e MAE no teste.
- [ ] Extrair e ordenar contribuição das variáveis (ranking).
- [ ] Escrever conclusão de P4 com a limitação do R² baixo.

---

## EP-04 — Comunicação executiva: relatório técnico e síntese (P0 · serve O5 · marco P3, peso 40%)
> Intento (PM): o gestor lê evidências, implicações, limitações e recomendações sem abrir o código.
> Cobre RF-12, RF-13. Inclui a seção do achado de governança 2024 + teto temporal como limitação (O6).

### US-11 — Relatório técnico em PDF (inclui achado 2024 + teto temporal) · 8 pts · depende de: US-05, US-06, US-07, US-08, US-10, US-18 · trace: RF-12, RF-14, O5, O6
**Como** pesquisador/gestor, **quero** um relatório técnico em PDF com pipeline, respostas P1–P5 com gráficos,
resultados do modelo, **a seção do achado de governança 2024** e as limitações, **para** ter o registro
completo e defensável da análise, com o teto temporal 2023 explicado.
> Subiu de 5→8 pts no remodel: agora integra a seção do achado 2024 (insumo de US-17/US-18) como
> limitação central, além das respostas P1–P5 e do modelo. 8 = teto INVEST; se inchar mais, fatiar a
> seção de governança numa story própria de redação.

**Critérios de aceite**
- **Dado** as análises P1–P5 e o modelo concluídos, **quando** montar o relatório, **então** o PDF cobre:
  pipeline de dados, cada resposta P1–P5 com gráfico, resultados do modelo (R²/MAE/ranking), conclusões e limitações.
- **Dado** o achado de governança 2024 (US-17/US-18), **quando** montar a seção de limitações, **então** o
  relatório tem uma **seção própria** que descreve as duas bases 2024 sem chave comum (LGPD/ANPD), lista as
  perguntas que morrem (P1/P4/P5 + raça×nota + sexo×nota) vs. sobrevivem (P2/P3 via RESULTADOS) e **justifica
  o teto temporal 2023** como decorrência da quebra.
- **Dado** o relatório, **quando** lido, **então** está em pt-BR, com visualizações legíveis, sem afirmação
  causal indevida e com o achado 2024 factualmente correto (conferido contra a fonte primária).

**Tasks**
- [ ] Estruturar o relatório (pipeline → P1–P5 → modelo → **achado de governança 2024** → conclusões → limitações).
- [ ] Inserir gráficos finais e estatísticas de cada pergunta.
- [ ] Redigir a seção do achado 2024 (a partir de US-17/US-18): duas bases, LGPD/ANPD, perguntas mortas vs. vivas, teto 2023.
- [ ] Redigir conclusões e seção de limitações (incl. R² baixo, não-causalidade, teto temporal 2023).
- [ ] Exportar para PDF e revisar com a dupla (conferir a seção 2024 contra a fonte primária).

### US-12 — Síntese executiva · 2 pts · depende de: US-11 · trace: RF-13, O5
**Como** gestor/equipe pedagógica, **quero** uma síntese executiva (problema → evidências → implicações → limitações → recomendações),
**para** decidir prioridades de intervenção sem ler o relatório técnico inteiro.

**Critérios de aceite**
- **Dado** o relatório técnico, **quando** abrir a síntese, **então** ela cobre, nessa ordem: problema, evidências,
  implicações, limitações (incl. o teto temporal 2023 / achado 2024) e recomendações — em linguagem acessível ao gestor.
- **Dado** a síntese, **quando** lida isolada, **então** comunica o achado principal sem depender do relatório técnico.

**Tasks**
- [ ] Destilar os achados-chave de P1–P5, do modelo e do achado de governança 2024.
- [ ] Escrever problema → evidências → implicações → limitações → recomendações.
- [ ] Revisar tom executivo e acessibilidade com a dupla.

---

## EP-05 — Reprodutibilidade do repositório (P0 · serve O5 · critério explícito de P3)
> Intento (PM): qualquer avaliador roda o projeto do zero pelo README e chega aos mesmos resultados.
> RNF-01/RNF-03 transversais, consolidados aqui.

### US-13 — Ambiente fixado e dados fora do versionamento · 2 pts · depende de: US-01 · trace: RNF-01, RNF-04
**Como** avaliador, **quero** o ambiente com dependências fixadas e os dados fora do Git,
**para** instalar o projeto de forma idêntica e sem baixar 1,7 GB indevidamente.

**Critérios de aceite**
- **Dado** o repositório, **quando** olhar as dependências, **então** elas estão fixadas (ex.: `requirements.txt`/`environment.yml` com versões).
- **Dado** o `.gitignore`, **quando** inspecionado, **então** `data/` (brutos e intermediários) nunca é versionado.

**Tasks**
- [ ] Fixar dependências com versões.
- [ ] Garantir `.gitignore` cobrindo `data/` e artefatos intermediários.
- [ ] Verificar que nenhum dado está versionado no histórico atual.

### US-14 — README com ordem de execução reprodutível · 3 pts · depende de: US-11, US-13 · trace: RNF-01, RNF-03, O5
**Como** avaliador, **quero** um README com a ordem de execução do pipeline,
**para** rodar tudo do zero e chegar aos mesmos resultados sem passo manual oculto.

**Critérios de aceite**
- **Dado** o README, **quando** seguido por alguém novo, **então** ele instala o ambiente, posiciona os dados e
  roda o pipeline na ordem correta até gerar análises/relatório — sem passo manual oculto.
- **Dado** um clone limpo, **quando** seguir o README, **então** chega aos mesmos resultados (reprodutibilidade verificada).
- **Dado** o módulo vivo (EP-07), **quando** ler o README, **então** existe um passo documentado para o avaliador
  ingerir uma edição nova (RESULTADOS) por conta própria e ver P2/P3 atualizados (RNF-03).

**Tasks**
- [ ] Documentar instalação do ambiente e onde colocar os dados.
- [ ] Documentar a ordem de execução (carga → tratamento → EDA → análises → modelo → relatório → dashboard).
- [ ] Documentar o passo de ingestão do módulo vivo (como rodar a rotina com um novo CSV RESULTADOS).
- [ ] Testar o passo a passo em ambiente limpo (revisão cruzada da dupla).

---

## EP-06 — Dashboard interativo Streamlit (P0 · serve O4)
> Intento (PM): gestor e jornalista exploram a desigualdade por ano/UF/escola/renda interativamente,
> com mapa por estado e correlação renda×nota. Cobre RF-10, RF-11.
> **Repriorizado P1 → P0 na 2ª remodelagem** — é a face "usável" exigida pelo professor. Deixou de
> ser "cede primeiro se o tempo apertar".

### US-15 — Dashboard Streamlit com filtros que atualizam visualizações · 5 pts · depende de: US-04 · trace: RF-10, O4
**Como** gestor/jornalista, **quero** um dashboard Streamlit com filtros de ano/UF/escola/renda que atualizam as visualizações,
**para** explorar a desigualdade interativamente.
> A edição viva ingerida pelo módulo vivo (EP-07) aparece como mais um valor no filtro de ano — ver US-22.

**Critérios de aceite**
- **Dado** o dashboard rodando localmente, **quando** ajustar qualquer um dos ≥4 filtros (ano, UF, tipo de escola, faixa de renda),
  **então** ≥4 visualizações se atualizam consistentemente com o filtro.
- **Dado** a base tratada, **quando** o dashboard carregar, **então** ele lê a base de forma eficiente (sem reprocessar bruto).
- **Dado** o filtro de ano, **quando** uma edição viva (P2/P3) tiver sido ingerida (EP-07), **então** o ano dela
  é selecionável sem quebrar as visões do núcleo SES (que seguem só 2022–2023).
- **Dado** o dashboard renderizado, **então** segue a referência visual definida (RNF-05): dark theme + fonte
  monospace + accent neon, gráficos **Plotly** (`plotly_dark`), KPI cards (`st.metric`) no topo e layout em grid com tabs.

**Tasks**
- [ ] Configurar `.streamlit/config.toml` (dark theme, primaryColor neon, font mono).
- [ ] Carregar a base tratada de forma eficiente (cache).
- [ ] Implementar os filtros: ano, UF, tipo de escola, faixa de renda.
- [ ] Implementar ≥4 visualizações reativas em **Plotly** (`plotly_dark`) — distribuições, comparação de grupos.
- [ ] Adicionar faixa de KPI cards (`st.metric`) no topo e layout em grid com `st.tabs`/`st.columns`.
- [ ] Validar que cada filtro atualiza as visualizações.
- [ ] Garantir que o filtro de ano comporta a(s) edição(ões) viva(s) de P2/P3 sem afetar as visões SES.

### US-16 — Mapa coroplético por estado e correlação renda×nota · 5 pts · depende de: US-15 · trace: RF-11, O4
**Como** gestor/jornalista, **quero** um mapa coroplético por estado e a correlação renda×nota no dashboard,
**para** ver a geografia da desigualdade e a relação renda×desempenho de forma visual.

**Critérios de aceite**
- **Dado** o dashboard, **quando** abrir o mapa, **então** exibe um coroplético por UF (estado) refletindo a métrica selecionada,
  respeitando os filtros ativos.
- **Dado** o dashboard, **quando** abrir a visão de correlação, **então** mostra a relação renda×nota com estatística de correlação.

**Tasks**
- [ ] Obter/usar a malha de UF do Brasil (GeoJSON de estados).
- [ ] Renderizar coroplético por estado com **Plotly** (`px.choropleth`, `plotly_dark`) reagindo aos filtros.
- [ ] Implementar visualização e estatística de correlação renda×nota (Plotly).
- [ ] Validar consistência mapa/correlação com os filtros.

> **Possível US-19 (em aberto — NÃO semeada):** visualização do achado 2024 no dashboard (ex.: linha do
> tempo janela linkada 2009–2023 × teto 2024). Briefing deixou em aberto; PRD trata como Premissa.
> Só entra se o PM/dupla aprovar no gate → dependeria de US-15. Ver "⚠️ Gaps para o PM".

---

## EP-07 — Módulo vivo: ingestão de edições novas nos eixos que sobrevivem à quebra (P2/P3) (P0 · serve O7)
> Intento (PM): permitir que o pesquisador/gestor alimente o produto com uma edição nova do ENEM (incl.
> 2024+) **só** nos eixos escola×nota (P2) e região×nota (P3) via RESULTADOS — carregando um CSV RESULTADOS,
> vendo P2/P3 recalculados e atualizados nas saídas — **sem reprocessar o núcleo SES 2022–2023**. Cobre
> RF-15, RF-16. Demonstração: ingestão de RESULTADOS 2024 (já baixado).
> **Desacoplamento é regra (RNF-07):** nenhuma story aqui pode reprocessar nem alterar o pipeline SES.
> Nenhum eixo SES (renda/preditores/perfil/raça/sexo) entra — só escola×região×nota. MVP = ingestão manual.
> **Fato confirmado em disco:** o layout DIFERE por edição — 2024 = dois CSVs separados em `DADOS/`
> (`PARTICIPANTES_2024.csv` + `RESULTADOS_2024.csv`); 2023 = único `MICRODADOS_ENEM_2023.csv`; 2022 = estrutura
> própria. O carregador (US-20) precisa abstrair essa diferença de layout por ano.

### US-20 — Carregador de edição parametrizável por ano (abstrai o layout que difere) · 5 pts · depende de: — · trace: RF-15, RNF-07, RNF-02
**Como** pesquisador, **quero** um carregador que receba uma edição (ano) e leia o RESULTADOS dela
independentemente de o layout daquele ano diferir dos outros, **para** ingerir edições novas sem reescrever
a leitura a cada ano.
> Independente do núcleo SES — é entrada nova e isolada (RNF-07). Não depende de US-01..US-04. Slice vertical:
> de "apontar para um ano" até "DataFrame de escola×nota normalizado", pronto para o recálculo (US-21).

**Critérios de aceite**
- **Dado** um identificador de edição (ex.: ano 2024) e o fato de que o layout difere por ano (2024 = dois CSVs
  em `DADOS/`; 2023 = CSV único; 2022 = estrutura própria), **quando** rodar o carregador, **então** ele localiza
  e lê o **RESULTADOS** daquela edição usando o mapeamento de layout correto, com leitura eficiente (`usecols`/`dtype`).
- **Dado** o RESULTADOS lido, **quando** o carregador normalizar, **então** devolve um DataFrame só com as colunas
  dos eixos que sobrevivem (identificação de escola/tipo de escola, UF/região, notas) e um marcador de `ano`,
  com nomes de coluna padronizados entre edições.
- **Dado** uma edição cujos headers/codificação de escola divergem do esperado, **quando** o carregador rodar,
  **então** a divergência é detectada e tratada como passo explícito (alinhamento/erro claro), não silenciada.
- **Dado** que o módulo é desacoplado, **quando** o carregador rodar, **então** ele **não** toca, lê nem reprocessa
  o pipeline do núcleo SES 2022–2023 (RNF-07).

**Tasks**
- [ ] Definir um mapeamento de layout por edição (qual arquivo é o RESULTADOS, onde fica, encoding/separador).
- [ ] Implementar leitura parametrizada por ano com `usecols`/`dtype` (eficiente — RNF-02).
- [ ] Normalizar para um schema-alvo: escola/tipo de escola, UF/região, notas, `ano` (nomes padronizados entre edições).
- [ ] Detectar e tratar divergência de headers/codificação de escola como passo explícito (não silenciar).
- [ ] Validar que a rotina é isolada do núcleo SES (ponto de entrada próprio, sem import do pipeline 2022–2023).

### US-21 — Recálculo de P2/P3 sobre a edição ingerida · 5 pts · depende de: US-20 · trace: RF-16, O7
**Como** gestor, **quero** que, ao ingerir uma edição nova, as visões de P2 (gap escola pública×privada) e
P3 (disparidade região×nota) sejam recalculadas para aquela edição, **para** ter as métricas dos eixos vivos
atualizadas com o dado mais recente.
> Reusa a lógica de P2/P3, mas operando sobre o DataFrame normalizado do carregador (não sobre a base SES).

**Critérios de aceite**
- **Dado** o DataFrame normalizado de uma edição (US-20), **quando** rodar o recálculo, **então** produz as
  métricas de **P2** (média/gap escola pública vs. privada) e **P3** (disparidade região×nota) para aquele `ano`.
- **Dado** que múltiplas edições foram ingeridas, **quando** consolidar, **então** as métricas de P2/P3 ficam
  empilhadas por `ano`, permitindo comparação entre edições (incl. lado a lado com 2022–2023).
- **Dado** o desacoplamento, **quando** o recálculo rodar, **então** ele opera **só** sobre os eixos que sobrevivem
  (escola/região×nota) e **não** reprocessa o núcleo SES (RNF-07).
- **Dado** o mesmo CSV de entrada, **quando** rodado de novo, **então** reproduz as mesmas métricas.

**Tasks**
- [ ] Implementar cálculo de P2 (média e gap pública×privada) sobre o DataFrame normalizado, por `ano`.
- [ ] Implementar cálculo de P3 (disparidade região×nota) sobre o DataFrame normalizado, por `ano`.
- [ ] Consolidar/empilhar as métricas por `ano` (saída comparável entre edições).
- [ ] Garantir reprodutibilidade e isolamento do núcleo SES.

### US-22 — Atualizar as saídas (dashboard/relatório) com a edição viva ingerida · 3 pts · depende de: US-21, US-15 · trace: RF-16, O7
**Como** gestor/jornalista, **quero** ver a edição viva ingerida refletida nas saídas (dashboard e/ou relatório),
**para** que o produto mostre P2/P3 atualizados, não só calcule nos bastidores.

**Critérios de aceite**
- **Dado** as métricas de P2/P3 recalculadas por edição (US-21), **quando** abrir o dashboard, **então** a edição
  viva aparece no filtro de ano e as visões de P2/P3 a exibem ao lado de 2022–2023.
- **Dado** o desacoplamento, **quando** a edição viva for exibida, **então** as visões do núcleo SES (P1/P4/P5)
  permanecem restritas a 2022–2023 e não são afetadas.
- **Dado** o produto, **quando** uma nova edição for ingerida (US-20→US-21), **então** as saídas refletem a nova
  edição **sem alteração de código manual** além de rodar a rotina de ingestão.

**Tasks**
- [ ] Ligar a saída consolidada de P2/P3 por `ano` (US-21) às visões do dashboard.
- [ ] Garantir que a edição viva entra no filtro de ano sem contaminar as visões SES.
- [ ] (Se o relatório exibir P2/P3 por edição) prever ponto de inserção das métricas vivas no relatório.
- [ ] Validar que ingerir uma edição nova atualiza as saídas só rodando a rotina (sem editar código).

### US-23 — Prova de conceito: ingerir RESULTADOS 2024 e exibir P2/P3 lado a lado com 2022–2023 · 3 pts · depende de: US-22 · trace: RF-15, RF-16, O7
**Como** gestor/pesquisador, **quero** rodar o módulo vivo de ponta a ponta sobre o **RESULTADOS 2024 real** e
ver escola×nota e região×nota de 2024 ao lado de 2022–2023, **para** provar que esses eixos sobrevivem à quebra
e que o produto não morre em 2023.
> É a métrica de O7 fechada como demonstração executável. Usa o arquivo 2024 já baixado (decisão do Augusto:
> prova de conceito com dado real, não arquitetura teórica).

**Critérios de aceite**
- **Dado** o `RESULTADOS_2024.csv` real (já baixado em `data/.../2024/`), **quando** rodar a rotina de ingestão
  ponta a ponta (US-20→US-21→US-22), **então** as métricas de P2 (escola×nota) e P3 (região×nota) de **2024**
  são produzidas e exibidas **ao lado** das de 2022–2023.
- **Dado** a prova de conceito, **quando** concluída, **então** o pipeline do núcleo SES 2022–2023 **não** foi
  tocado nem reprocessado para isso (RNF-07) — verificável.
- **Dado** os headers reais de RESULTADOS 2024, **quando** a ingestão rodar, **então** qualquer divergência de
  codificação de escola/UF foi tratada no passo de alinhamento (US-20) e está documentada.

**Tasks**
- [ ] Apontar o carregador para a edição 2024 (RESULTADOS_2024.csv real, layout de dois CSVs em `DADOS/`).
- [ ] Validar headers/codificação reais de 2024 vs. 2022–2023; documentar divergências e o alinhamento aplicado.
- [ ] Rodar US-20→US-21→US-22 ponta a ponta para 2024.
- [ ] Conferir P2/P3 de 2024 exibidos ao lado de 2022–2023 e registrar a evidência da demonstração.
- [ ] Confirmar (e registrar) que o núcleo SES não foi reprocessado.

---

## Ordem recomendada (respeita dependências e prioridade — todos P0)
US-01 → US-02 → US-03 → (US-13 em paralelo) → US-04 →
{US-05, US-06, US-07, US-08} (paralelizáveis entre a dupla) →
US-09 → US-10 →
(US-17 → US-18 em paralelo desde o início — independentes do pipeline 2022–2023) →
(US-20 também paralelizável desde o início — entrada isolada do módulo vivo) →
US-15 → US-16 (dashboard, agora P0) →
US-21 → US-22 → US-23 (módulo vivo: recálculo → saídas → prova de conceito 2024) →
US-11 → US-12 → US-14 (relatório/síntese/README por último, consolidam tudo).
