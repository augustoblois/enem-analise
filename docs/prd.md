# PRD — Análise dos Microdados do ENEM (Desigualdade Socioeconômica × Desempenho)

> Fonte: docs/briefing.md (aprovado). Gerado pelo pm-agent.
> Projeto acadêmico de Data Science (disciplina Análise de Dados, UFPB / PSAE00263 - T01).
> NÃO é web-app: o "produto" é um pipeline Python + dashboard Streamlit + relatório PDF + síntese executiva.
> **Remodelado em 2026-06-19** após descoberta da quebra de linkage nos microdados 2024 (ver Problema & visão, O6, escopo "Fora", RF-14 e EP-02b). Estrutura e demais seções preservadas do PRD anterior.
> **2ª remodelagem em 2026-06-19** — o professor exige um **produto USÁVEL** (não só análise estática). Adicionado o **módulo vivo** nos eixos que sobrevivem à quebra (escola×região×nota via RESULTADOS), capaz de ingerir edições novas incl. 2024+ (ver Problema & visão, O7, escopo "Em escopo", RF-15/RF-16, EP-07). Núcleo SES (P1/P4/P5) segue congelado em 2022–2023 — não muda.

## ⚠️ Gaps para o gate
- **Datas exatas de P2 e P3 não definidas** no briefing (dependem do cronograma oficial da turma no SIGAA, PSAE00263 - T01). Os marcos de entrega abaixo estão atrelados a P2/P3 por conteúdo, não por data. Confirmar antes de planejar sprints.
- **Cadência/forma da ingestão do módulo vivo está "A definir"** no briefing (ingestão manual de novo CSV vs. automatizada; quais edições além de 2024 entram no MVP). O escopo do módulo vivo (O7, EP-07, RF-15/RF-16) assume ingestão **manual de um CSV RESULTADOS de nova edição** como MVP, com 2024 como prova de conceito — ver Premissas. Confirmar no gate se o professor espera algo automatizado (pull do INEP / agendamento), o que ampliaria o escopo.

## Problema & visão
A educação brasileira reproduz desigualdades estruturais: candidatos de maior renda, filhos de pais com ensino superior, de escolas privadas e de regiões mais ricas superam sistematicamente os demais no ENEM. A magnitude exata dessas diferenças, sua variação no tempo e os fatores que mais as explicam seguem pouco explorados de forma integrada e visual — e gestores de política pública educacional precisam priorizar investimento e ações afirmativas sem evidência quantitativa consolidada. Este projeto transforma os microdados do ENEM num produto analítico que quantifica, visualiza e comunica como fatores socioeconômicos determinam o desempenho, com foco no Nordeste, para apoiar essa decisão. O núcleo analítico das 5 perguntas é a janela recente **linkada 2022–2023** (questionário + nota na mesma linha), enquadrada na janela viável/defensável **2009–2023** (pós-reformulação metodológica e pré-quebra de linkage — não significa ingerir todas as 14 edições). A partir de **2024** o INEP separou os microdados em duas bases sem chave comum (proteção LGPD validada pela ANPD), cortando o pareamento SES↔nota do mesmo indivíduo: isso fixa o **teto temporal em 2023** e torna a própria quebra um **achado central de governança de dados**, não uma nota de rodapé. Além de retrospectivo, o produto precisa ser **usável e vivo** (exigência explícita do professor): nos eixos que sobrevivem à quebra — **escola×nota e região×nota (P2/P3), via RESULTADOS** — ele deve **ingerir edições novas do ENEM (incl. 2024+) sem reprocessar o núcleo SES**, mantendo essas visões atualizadas. O núcleo SES (P1/P4/P5) permanece rico mas congelado em 2022–2023 por imposição do dado; o próprio achado de 2024 justifica por que apenas escola×região×nota podem viver.

## Objetivos (mensuráveis)
- **O1 — Responder as 5 perguntas analíticas (P1–P5) com evidência estatística, no núcleo linkado 2022–2023.** · métrica: cada uma de P1–P5 tem, no relatório, ao menos uma visualização e uma estatística de suporte (média/gap/coeficiente/correlação) e uma conclusão escrita; nenhuma pergunta fica sem resposta sustentada por número.
- **O2 — Entregar base analítica tratada, integrada e documentada (marco P2 — 20%).** · métrica: dataset 2022+2023 unificado, com dicionário de variáveis usadas, tratamento de nulos/tipos documentado e EDA inicial; rodável do zero.
- **O3 — Entregar modelo preditivo interpretável para P4.** · métrica: regressão linear treinada com R² e MAE reportados em conjunto de teste (referência R²≈0,30 do entrega1.pdf) e ranking de variáveis por contribuição.
- **O4 — Entregar dashboard Streamlit interativo.** · métrica: ≥4 filtros funcionais (ano, UF, tipo de escola, faixa de renda) que atualizam ≥4 visualizações, incluindo mapa coroplético por estado e correlação renda×nota.
- **O5 — Entregar comunicação executiva e reprodutibilidade (marco P3 — 40%).** · métrica: relatório técnico em PDF + síntese executiva (problema → evidências → implicações → limitações → recomendações), e o repositório roda do zero seguindo o README sem passos manuais ocultos.
- **O6 — Documentar a quebra de linkage 2024 como achado de governança de dados.** · métrica: seção própria no relatório (e, se decidido, no dashboard) que, com correção factual, descreve as duas bases 2024 sem chave comum (PARTICIPANTES = questionário/renda/demografia, sem nota/escola; RESULTADOS = escola/notas, sem questionário/demografia), cita a base ANPD/LGPD, identifica quais perguntas morrem em 2024+ (P1, P4, P5 + raça×nota + sexo×nota) e quais sobrevivem via RESULTADOS (P2, P3 — escola×nota, região×nota), e justifica o teto temporal 2023.
- **O7 — Entregar um módulo vivo, usável, nos eixos que sobrevivem à quebra (escola×nota e região×nota — P2/P3, via RESULTADOS), capaz de ingerir edições novas do ENEM sem reprocessar o núcleo SES.** · métrica: ingerir um CSV RESULTADOS de uma edição nova (prova de conceito: **RESULTADOS 2024**) e ter as visões de P2 (escola×nota) e P3 (região×nota) recalculadas e atualizadas nas saídas (dashboard e/ou relatório) **sem tocar no pipeline do núcleo SES 2022–2023** — verificável: rodar a rotina de ingestão sobre 2024 produz métricas escola×nota e região×nota para 2024 ao lado das de 2022–2023.

## Personas
- **Gestor de política pública educacional (MEC / secretarias)** — PRIMÁRIO, tomador de decisão · job: identificar regiões e perfis prioritários para intervenção, com base em evidência, para alocar investimento e ações afirmativas.
- **Pesquisador / docente de educação** — secundário · job: usar a base analítica e os achados (inclusive a limitação de governança de 2024) como insumo para estudos sobre desigualdade escolar.
- **Equipe pedagógica de escola pública** — secundário · job: contextualizar o desempenho dos alunos frente ao perfil socioeconômico.
- **Jornalista de dados / comunicador** — secundário · job: produzir narrativas visuais sobre equidade educacional e sobre o impacto da proteção de dados na transparência pública.

## Escopo
**Em escopo**
- Aquisição, tratamento, integração e documentação dos microdados ENEM 2022 e 2023 (núcleo linkado das 5 perguntas).
- Base analítica tratada (seleção e recodificação das variáveis socioeconômicas e de nota relevantes).
- EDA (distribuições, comparações de grupos, correlações).
- Respostas às 5 perguntas P1–P5 com estatística + visualização, no núcleo 2022–2023.
- Modelo preditivo P4: regressão linear (interpretável), com R² e MAE.
- Dashboard interativo em Streamlit com filtros e mapa coroplético por estado.
- Relatório técnico em PDF e síntese executiva.
- **Documentação do achado de governança 2024** (quebra de linkage LGPD/ANPD): seção factual no relatório definindo o teto temporal e a limitação metodológica.
- **Módulo vivo — ingestão de edições novas nos eixos que sobrevivem à quebra (P2/P3): escola×nota e região×nota via RESULTADOS.** Rotina capaz de carregar um CSV RESULTADOS de edição nova (incl. **2024+**), recalcular as métricas de P2/P3 e atualizar as saídas (dashboard/relatório), **sem reprocessar o núcleo SES 2022–2023**. Demonstração mínima: ingestão de **RESULTADOS 2024** como prova de conceito de que esses eixos sobrevivem à quebra.
- Repositório reprodutível (README, ambiente, ordem de execução).

**Fora de escopo / não-objetivos**
- **Análise SES×nota (renda, preditores, perfil) em 2024 e edições posteriores** — impossível parear perfil socioeconômico ↔ nota do mesmo indivíduo (INEP separou PARTICIPANTES e RESULTADOS sem chave comum, por LGPD/ANPD). P1/P4/P5 + raça×nota + sexo×nota **não** entram no módulo vivo: 2024+ só aparece nesses eixos como achado/limitação documentada (O6), nunca como dado analisado. **O que vive é exclusivamente escola×região×nota (P2/P3) via RESULTADOS.**
- Inferência causal rigorosa além de controles simples (ex.: controlar renda/tipo de escola em P3) — não se afirma causalidade.
- Séries históricas longas / ingestão de todas as edições da janela 2009–2023 — a janela 2009–2023 é o enquadramento *viável* da tese; o núcleo analisado é 2022–2023.
- Modelos complexos além de regressão linear (sem random forest, gradient boosting, redes neurais) — decisão de escopo a favor de interpretabilidade.
- Deploy/hospedagem pública do dashboard (rodar localmente é suficiente para a disciplina).
- Dado individual sensível/reidentificação — microdados são anonimizados e assim permanecem.
- Recipes web (frontend, auth, SEO, Vercel, etc.): não se aplica a este projeto.

## Requisitos funcionais
- **RF-01 — Adquirir e carregar os microdados 2022 e 2023 de forma eficiente** (leitura com tipagem/seleção de colunas e, se necessário, amostragem). · persona: pesquisador · serve: O2
- **RF-02 — Tratar e integrar os dados** (nulos, tipos, recodificação de variáveis socioeconômicas, unificação 2022+2023 com marcador de ano). · persona: pesquisador · serve: O2
- **RF-03 — Documentar a base analítica** (dicionário das variáveis usadas, decisões de tratamento). · persona: pesquisador · serve: O2
- **RF-04 — Realizar EDA inicial** (distribuições de nota, perfis socioeconômicos, comparações de grupo). · persona: pesquisador · serve: O2
- **RF-05 — Responder P1** (renda × nota média nas 5 áreas, com estatística e gráfico). · persona: gestor · serve: O1
- **RF-06 — Responder P2** (gap escola pública vs. privada e sua variação 2022→2023). · persona: gestor · serve: O1
- **RF-07 — Responder P3** (disparidade regional Nordeste vs. Sul/Sudeste, controlando renda e tipo de escola). · persona: gestor · serve: O1
- **RF-08 — Responder P4** (modelo de regressão linear: variáveis socioeconômicas que melhor predizem desempenho, com R²/MAE e ranking). · persona: gestor · serve: O1, O3
- **RF-09 — Responder P5** (perfil socioeconômico dos candidatos com nota 1000 na Redação). · persona: gestor · serve: O1
- **RF-10 — Disponibilizar dashboard Streamlit com filtros** (ano/UF/escola/renda) que atualizam as visualizações. · persona: gestor, jornalista · serve: O4
- **RF-11 — Exibir mapa coroplético por estado e correlação renda×nota no dashboard.** · persona: gestor, jornalista · serve: O4
- **RF-12 — Gerar relatório técnico em PDF** (pipeline, respostas P1–P5 com gráficos, resultados do modelo, conclusões e limitações). · persona: pesquisador, gestor · serve: O5
- **RF-13 — Produzir síntese executiva** (problema, evidências, implicações, limitações, recomendações). · persona: gestor, equipe pedagógica · serve: O5
- **RF-14 — Documentar e comunicar o achado de governança 2024** (seção factual: duas bases sem chave comum, base LGPD/ANPD, perguntas que morrem [P1/P4/P5 + raça×nota + sexo×nota] vs. sobrevivem [P2/P3 via RESULTADOS], teto temporal 2023, limitação metodológica). Fonte documental: `Leia_Me_Enem_2024.pdf` (INEP, jun/2025). · persona: pesquisador, gestor, jornalista · serve: O6
- **RF-15 — Ingerir incrementalmente uma edição nova do ENEM no módulo vivo** (carregar um CSV RESULTADOS de edição nova — incl. 2024+ —, validar/alinhar colunas de escola e nota, e anexar a edição às bases dos eixos P2/P3 com marcador de ano) **sem reprocessar o pipeline do núcleo SES 2022–2023**. Prova de conceito: ingestão de **RESULTADOS 2024**. · persona: pesquisador, gestor · serve: O7
- **RF-16 — Recalcular e atualizar as visões P2/P3 a partir da edição ingerida** (gap escola pública×privada e disparidade região×nota recalculados para a nova edição e exibidos ao lado das edições anteriores no dashboard e/ou nas saídas do relatório). · persona: gestor, jornalista · serve: O7

## Requisitos não-funcionais
- **RNF-01 — Reprodutibilidade:** o projeto roda do zero seguindo o README (ambiente, dependências fixadas, ordem de execução); sem passo manual oculto. Critério explícito de P3.
- **RNF-02 — Performance de dados:** CSVs de ~1,7 GB por edição exigem leitura eficiente (seleção de colunas, tipagem/`dtype`, chunking ou amostragem documentada); o pipeline deve rodar em máquina comum sem estourar memória.
- **RNF-03 — Documentação:** código compreensível, dicionário de variáveis e decisões de tratamento registradas; a dupla deve poder defender cada trecho. A rotina de ingestão do módulo vivo (RF-15) deve ter passo documentado para o avaliador repetir com um novo CSV.
- **RNF-04 — Ética / governança de dados:** uso responsável dos microdados anonimizados, sem reidentificação; declarar uso de IA com impacto relevante; dados nunca versionados (`.gitignore`). A quebra de 2024 é tratada como caso de governança (LGPD/ANPD) com correção factual, não como julgamento.
- **RNF-05 — Qualidade de comunicação visual:** visualizações legíveis seguindo boas práticas de dataviz (eixos, legendas, escala honesta), em pt-BR. **Referência visual definida (2026-06-19): estética techy/moderna** — dashboard Streamlit dark theme + fonte monospace + accent neon, gráficos **Plotly** interativos (`plotly_dark`), KPI cards (`st.metric`) no topo, layout em grid com tabs por pergunta, mapa coroplético Plotly. **Plotly é a lib de gráficos do dashboard; matplotlib/seaborn ficam restritos ao relatório PDF.**
- **RNF-06 — Idioma:** todos os entregáveis em pt-BR; termos técnicos e identificadores de código exatos.
- **RNF-07 — Extensibilidade do módulo vivo:** a ingestão de nova edição (RF-15/RF-16) deve ser desacoplada do núcleo SES — adicionar uma edição nos eixos P2/P3 não pode exigir reprocessar nem alterar a análise SES 2022–2023; o ponto de entrada da nova edição é claro e isolado.

## Épicos
> O PM é dono dos épicos; o scrum-master fatia em stories. Ordenados por prioridade. Mapeados aos marcos da disciplina (P2 = dados+EDA; P3 = análise+modelo+dashboard+relatório+reprodutibilidade).

- **EP-01 — Base analítica: aquisição, tratamento, integração e documentação dos dados** · `P0` · serve: O2 · intento (outcome): permitir que o pesquisador parta de uma base ENEM 2022–2023 limpa, integrada e documentada — sem reprocessar CSVs brutos de 1,7 GB a cada análise. *(marco P2)* — cobre RF-01, RF-02, RF-03.
- **EP-02 — EDA e respostas às perguntas analíticas P1–P5** · `P0` · serve: O1 · intento (outcome): permitir que o gestor tenha cada uma das 5 perguntas respondida com número e gráfico, entendendo magnitude e tendência da desigualdade no núcleo linkado 2022–2023. — cobre RF-04, RF-05, RF-06, RF-07, RF-09.
- **EP-02b — Achado de governança 2024: quebra do linkage SES↔nota** · `P0` · serve: O6 · intento (outcome): permitir que o gestor e o pesquisador entendam, com correção factual, por que a análise SES×desempenho para em 2023 — as duas bases 2024 sem chave comum (LGPD/ANPD), quais perguntas deixam de ser respondíveis (P1/P4/P5 + raça×nota + sexo×nota) e quais sobrevivem (P2/P3 via RESULTADOS) — transformando a limitação em contribuição (rigor + utilidade). — cobre RF-14.
- **EP-03 — Modelagem preditiva interpretável (P4)** · `P0` · serve: O3, O1 · intento (outcome): permitir que o gestor veja quais fatores socioeconômicos combinados mais predizem desempenho, com erro (MAE/R²) e ranking de variáveis explícitos. — cobre RF-08.
- **EP-04 — Comunicação executiva: relatório técnico e síntese** · `P0` · serve: O5 · intento (outcome): permitir que o gestor leia evidências, implicações, limitações e recomendações sem precisar abrir o código. *(marco P3, peso 40%)* — cobre RF-12, RF-13.
- **EP-05 — Reprodutibilidade do repositório** · `P0` · serve: O5 · intento (outcome): permitir que qualquer avaliador rode o projeto do zero pelo README e chegue aos mesmos resultados. *(critério explícito de P3)* — RNF-01/RNF-03 transversais; consolidado neste épico.
- **EP-06 — Dashboard interativo Streamlit** · `P0` · serve: O4 · intento (outcome): permitir que o gestor e o jornalista explorem a desigualdade por ano/UF/escola/renda interativamente, incluindo mapa por estado e correlação renda×nota — sendo a face "usável" do produto que o professor exige. — cobre RF-10, RF-11.
- **EP-07 — Módulo vivo: ingestão de edições novas nos eixos que sobrevivem à quebra (P2/P3)** · `P0` · serve: O7 · intento (outcome): permitir que o pesquisador/gestor alimente o produto com uma edição nova do ENEM (incl. 2024+) nos eixos escola×nota e região×nota — carregando um CSV RESULTADOS e vendo P2/P3 recalculados e atualizados nas saídas — **sem reprocessar o núcleo SES 2022–2023**, fazendo do produto algo que sobrevive à quebra e não morre em 2023. Demonstração: ingestão de RESULTADOS 2024. — cobre RF-15, RF-16.

## Premissas
- **Dashboard repriorizado para `P0`:** na 1ª remodelagem o dashboard era `P1` (cederia primeiro se o tempo apertasse). Com a exigência explícita do professor de um **produto usável**, o dashboard deixa de ser "desejável" e vira parte central da entrega — elevei EP-06 para `P0`. Se a dupla discordar (preferir proteger relatório+reprodutibilidade acima de tudo), corrigir no gate.
- **MVP do módulo vivo = ingestão manual de um CSV RESULTADOS de nova edição**, com **2024 como prova de conceito**. O briefing deixa "A definir" a cadência (manual vs. automatizada) e quais edições além de 2024 entram. Assumi o caminho mínimo defensável (manual, 1 edição de demonstração); automação/pull do INEP fica fora do MVP até decisão no gate — ver Gap no topo.
- **Eixos do módulo vivo = exclusivamente P2 (escola×nota) e P3 (região×nota) via RESULTADOS.** É o que sobrevive à quebra; nenhum eixo SES (renda/preditores/perfil/raça/sexo) entra, por imposição do dado.
- **Variável-alvo do modelo P4:** assumida como a nota (média das áreas ou nota por área a definir na modelagem); o briefing não fixa a definição exata do alvo. A escolha será documentada no relatório.
- **Faixas de renda e variáveis socioeconômicas** seguem o dicionário do INEP (questionário socioeconômico); recodificações específicas serão documentadas (RF-03).
- **Mapa coroplético** usa malha de UF do Brasil (estados); granularidade municipal está fora de escopo.
- **Local do achado de governança 2024:** assumido como seção própria no relatório (RF-14). Se ganha visualização própria no dashboard (ex.: linha do tempo janela linkada × teto 2024) é decisão em aberto — ver "A definir" do briefing; corrigir no gate.

## Riscos & dependências
- **Volume de dados (~1,7 GB/edição):** risco de performance/memória; mitigado por RNF-02 (tipagem, seleção de colunas, amostragem documentada). Dependência: dados já baixados em `data/microdados_enem_2022/` e `2023/`.
- **R² baixo esperado (~0,30):** regressão linear sobre fatores socioeconômicos explica parte limitada da variância; é resultado legítimo e deve ser comunicado como limitação, não como falha.
- **Cronograma indefinido (P2/P3):** sem datas oficiais (SIGAA), o planejamento de sprints fica aberto — ver Gap no topo.
- **Comparabilidade 2022 vs. 2023:** mudanças de questionário/codificação entre edições podem dificultar a integração; validar antes de unificar (RF-02). Nota: a separação de bases é um fato **de 2024**, verificado nos headers reais; as edições 2022–2023 mantêm questionário + notas na mesma linha (linkadas), portanto a quebra **não afeta o núcleo 2022–2023**.
- **Comparabilidade da edição 2024 RESULTADOS com 2022–2023 (módulo vivo):** a ingestão (RF-15/RF-16) assume que escola e nota seguem coabitando em RESULTADOS nas edições novas e que a codificação de escola/UF é alinhável com 2022–2023. Mudanças de layout/codificação de escola em 2024+ (ou em edições futuras) podem quebrar o recálculo de P2/P3 — validar headers e codificação da edição antes de anexar; tratar divergências de codificação como passo explícito da rotina de ingestão. Risco residual: uma edição futura pode também remover a escola de RESULTADOS, encerrando o módulo vivo — documentar essa dependência.
- **Correção factual do achado 2024 (RF-14):** depende de citar fielmente o `Leia_Me_Enem_2024.pdf` (INEP, jun/2025) e a base LGPD/ANPD; risco de imprecisão factual se a fonte não for conferida diretamente — mitigar lendo o Leia-Me antes de redigir a seção.

## Autoavaliação (handoff)
- **Parte mais fraca:** o MVP do módulo vivo (EP-07) é o trecho mais frágil — repousa em duas suposições não confirmadas: (a) a cadência "ingestão manual, 1 edição de demonstração" (o professor pode esperar automação) e (b) a hipótese de que escola+nota e a codificação de escola permanecem compatíveis em RESULTADOS 2024. Se (b) falhar na validação dos headers de 2024, RF-15/RF-16 precisam de retrabalho antes de virar story segura.
- **O que mais reduziria a incerteza:** confirmar a cadência esperada do módulo vivo (manual vs. automatizada) e validar os headers reais de RESULTADOS 2024 — juntos definem se EP-07 é uma rotina simples de append ou um trabalho de reconciliação de schema. Em segundo lugar, as datas oficiais de P2/P3 (SIGAA) para dar ordem temporal aos sprints.
- **O que ainda depende de suposição:** a cadência e os eixos-extra do módulo vivo (Premissa, briefing "A definir"), a repriorização do dashboard para P0 (Premissa, contra o "peso igual" do briefing), a compatibilidade de RESULTADOS 2024, a definição do alvo/variáveis do P4 e o local do achado 2024 (relatório vs. também dashboard). Todos passíveis de correção no gate.
