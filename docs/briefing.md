# Briefing — Análise dos Microdados do ENEM (Desigualdade Socioeconômica × Desempenho)

> Fonte de intenção (entrevista de discovery). Gerado por briefing-intake.
> Insumo do pm-agent (write-prd). Não contém metas medíveis nem épicos — isso é o PRD.
> Base documental: `docs/entrega1.pdf` (Projeto 1 / P1, já entregue) + `aula01-intro.pdf` (rubrica da disciplina).
> **Remodelado em 2026-06-19** após descoberta crítica de quebra de linkage nos microdados 2024 (ver "Mudança de circunstância" abaixo). Fonte do pivot: `vault/academic/analise-dados.md` + `Leia_Me_Enem_2024.pdf` (INEP, jun/2025).
> **2ª remodelagem em 2026-06-19** — o professor explicitou que quer um **produto usável** (não só análise estática). Resposta de escopo: manter o núcleo SES rico em 2022–2023 E adicionar um **módulo vivo** nos eixos que sobrevivem à quebra (escola×região×nota via RESULTADOS), capaz de ingerir edições novas incl. 2024+. Ver "Decisões de escopo".

## Mudança de circunstância (2026-06-19) — por que o escopo mudou
A partir da **edição 2024**, o INEP dividiu os microdados em duas bases **sem chave de ligação em comum** (proteção LGPD validada pela ANPD): `PARTICIPANTES_2024.csv` (questionário socioeconômico + demografia, **sem nota, sem escola**) e `RESULTADOS_2024.csv` (escola + todas as notas, **sem questionário, sem demografia**). É **impossível parear perfil socioeconômico ↔ nota do mesmo indivíduo de 2024 em diante** — o join foi cortado de propósito, não há solução de engenharia.

Consequência para o projeto: a análise SES×desempenho tem **teto temporal em 2023**. As edições **2020–2023 mantêm questionário + notas na mesma linha (linkadas)**, verificado nos headers reais; a separação em duas bases é nova em 2024. A tese fica recortada para a **janela linkada 2009–2023** (era pós-reformulação metodológica e pré-quebra do linkage), e a própria quebra de 2024 vira **achado central de governança de dados** — alinhado à rubrica (rigor + limitações + utilidade).

## Em uma frase
Transformar os microdados do ENEM em um produto analítico que quantifica, visualiza e comunica como fatores socioeconômicos (renda, tipo de escola, região, escolaridade dos pais) determinam o desempenho — com foco no Nordeste — para apoiar decisão de política pública educacional; tendo como núcleo a janela recente linkada **2022–2023** (dentro da janela viável 2009–2023), documentando a **quebra do linkage socioeconômico em 2024** como achado de governança de dados, e entregando um **produto usável** cujo módulo de escola×região×nota permanece vivo (ingere edições novas, incl. 2024+, via RESULTADOS) mesmo após a quebra.

## Problema
A educação brasileira reproduz desigualdades estruturais: candidatos de maior renda, filhos de pais com ensino superior, de escolas privadas e de regiões mais ricas superam sistematicamente os demais. A magnitude exata dessas diferenças, sua variação no tempo e os fatores que mais as explicam seguem pouco explorados de forma integrada e visual. Quem sente a dor: gestores que precisam priorizar investimento e ações afirmativas mas carecem de evidência quantitativa consolidada. Por que agora: os microdados 2022–2023 permitem recorte comparativo recente e linkado — e, simultaneamente, a quebra de 2024 fecha essa janela, tornando urgente registrar o que ainda é analisável e por quê.

## Público / personas
- **Gestor de política pública educacional (MEC / secretarias estaduais)** — PRIMÁRIO e tomador de decisão · job: identificar regiões e perfis prioritários para intervenção, com base em evidência, para alocar investimento e ações afirmativas.
- **Pesquisador / docente de educação** — secundário · job: usar a base analítica e os achados (inclusive a limitação de governança de 2024) como insumo para estudos sobre desigualdade escolar.
- **Equipe pedagógica de escola pública** — secundário · job: contextualizar o desempenho dos alunos frente ao perfil socioeconômico.
- **Jornalista de dados / comunicador** — secundário · job: produzir narrativas visuais sobre equidade educacional e sobre o impacto da proteção de dados na transparência pública.

## O que o cliente quer (intenção, não requisito)
- Responder 5 perguntas analíticas (núcleo 2022–2023):
  - **P1** — relação entre faixa de renda familiar e nota média nas 5 áreas.
  - **P2** — gap escola pública vs. privada e se variou entre 2022 e 2023.
  - **P3** — disparidade regional (Nordeste vs. Sul/Sudeste) e se persiste controlando renda e tipo de escola.
  - **P4** — quais variáveis socioeconômicas, combinadas, melhor predizem o desempenho.
  - **P5** — perfil socioeconômico dos candidatos com nota 1000 na Redação.
- Documentar a **quebra do linkage socioeconômico em 2024** como achado central: o que mudou (duas bases sem chave comum), por que P1/P4/P5 (e raça×nota, sexo×nota) deixam de ser respondíveis em 2024+, enquanto P2/P3 (escola×nota, região×nota via RESULTADOS) sobrevivem; e o que isso define como teto temporal e como limitação metodológica.
- Um **produto usável** (pedido explícito do professor), não só análise estática: um **módulo vivo** nos eixos que sobrevivem à quebra de 2024 — escola×nota e região×nota (P2/P3, via RESULTADOS) — capaz de ingerir edições novas do ENEM (incl. 2024+) e seguir respondendo sem reprocessamento manual. O núcleo SES (P1/P4/P5) permanece rico mas congelado em 2022–2023 por imposição do dado.
- Dashboard interativo (Streamlit): filtros por ano/UF/escola/renda, distribuições, comparação de grupos, mapa coroplético por estado, correlação renda×nota.
- Relatório técnico (PDF): pipeline de dados, respostas às 5 perguntas com gráficos, resultados do modelo preditivo (R²/MAE), achado de governança 2024, conclusões e limitações.
- Síntese executiva: problema, evidências, implicações, limitações e recomendações (exigência do produto mínimo da disciplina).

## Decisões de escopo (do fork)
- Tipo de produto: **produto analítico de dados** (não web fullstack) — pipeline Python + dashboard Streamlit + relatório PDF.
- Recipes (web): **nenhum** — fase de governança apenas; sem scaffold/build do Project Conduction.
- **Janela analítica das 5 perguntas: núcleo 2022–2023** (edições linkadas, headers verificados). A janela **2009–2023** entra como a janela *viável/defensável* da tese (não significa ingerir todas as 14 edições) — o recorte 2022–2023 é o comparativo recente dentro dela.
- **Teto temporal do núcleo SES: 2023.** A análise SES×desempenho (P1/P4/P5) **não** estende para 2024+ (linkage cortado) — fica congelada em 2022–2023 por imposição do dado.
- **Módulo vivo (decisão da 2ª remodelagem — produto usável):** os eixos escola×nota e região×nota (P2/P3) sobrevivem à quebra porque escola e nota convivem em RESULTADOS. Esse módulo **entra no escopo central** e deve ingerir edições novas do ENEM (incl. 2024+) — é a parte "usável que não morre" que o professor pediu. O achado de 2024 justifica *por que* só esses eixos podem viver.
- **Achado da quebra 2024: central + limitação** — vira seção própria do produto (documenta ANPD/LGPD, por que perguntas morrem, teto temporal), não apenas uma nota de rodapé.
- Entregáveis prioritários: **dashboard e relatório com peso igual** (sem priorização se o tempo apertar).
- Escopo de modelagem (P4): **somente regressão linear** — foco em interpretabilidade (R²≈0,30, MAE), como no entrega1.pdf.
- Prazo: **sem pressa / muito tempo restante** — entregas progressivas até o fim do semestre (ver Restrições).

## Restrições
- Idiomas: português (pt-BR).
- Orçamento: não se aplica (projeto acadêmico).
- Equipe: Augusto Blois + Pedro Flávio Nogueira Ribeiro de Luna (dupla).
- Stack: Python 3.11+, pandas, numpy, matplotlib/seaborn, scikit-learn, Streamlit, Jupyter.
- Dados: Microdados ENEM 2022 e 2023 (INEP), públicos, linkados (questionário + notas na mesma linha). Já baixados em `data/microdados_enem_2022/` e `data/microdados_enem_2023/` (CSV + dicionário). ~1,7 GB CSV por edição — `.gitignore` exclui dados (nunca versionar). O `Leia_Me_Enem_2024.pdf` (INEP) é fonte documental do achado de governança, mas a edição 2024 **não** entra na análise SES×desempenho.
- **Critérios de avaliação da disciplina (o que o professor mais valoriza)** — a nota reflete **processo, rigor, execução técnica, utilidade da solução e comunicação**. Pesos: P1 10% (já entregue), **P2 20%** (aquisição/tratamento/integração/documentação dos dados + EDA inicial), **P3 40%** (análise consolidada, visualizações, comunicação executiva, recomendações e **reprodutibilidade**). Projeto = 70% da nota. O achado de governança 2024 reforça diretamente o eixo "rigor + limitações".
- Produto mínimo exigido: (1) repositório organizado e reprodutível, (2) base analítica tratada/documentada, (3) relatório técnico, (4) visualizações, (5) síntese executiva.
- **Exigência adicional do professor: produto USÁVEL** — não basta análise estática; ele quer algo que funcione como produto de fato. Atendido pelo módulo vivo (P2/P3 ingere edições novas) + dashboard interativo, não por extensão futura do núcleo SES (impossível). Augusto considera a exigência exagerada para o contexto, mas é restrição dada.
- Ética/governança: uso responsável; declarar uso de IA com impacto relevante; todo código deve ser compreendido e defendido pela equipe. Microdados são anonimizados (sem dado sensível identificado). A quebra de 2024 é ela própria um caso de governança de dados (LGPD/ANPD) a ser tratado com correção factual.
- Referências visuais (definido 2026-06-19): estética **"techy/moderna"** — dashboard Streamlit dark theme, fonte monospace, accent neon (ex.: verde/ciano), gráficos **Plotly** interativos (`plotly_dark`), KPI cards (`st.metric`) no topo, layout em grid com tabs por pergunta, mapa coroplético Plotly. Matplotlib/seaborn ficam restritos ao relatório PDF. Seguir boas práticas de dataviz (escala honesta, legendas, eixos).

## Calendário (entregas progressivas)
- **P1 — Projeto 1 (entregue):** problema, fontes, perguntas, desenho do produto, plano. = `docs/entrega1.pdf`.
- **19/06/2026 (hoje):** apresentação da ideia do projeto — não é entrega avaliada de produto, apenas exposição da proposta.
- **P2 — Projeto 2 (próxima):** aquisição, tratamento, integração, documentação dos dados + EDA inicial. Data exata: a definir.
- **P3 — Projeto Final:** análise consolidada, dashboard, relatório, síntese executiva, reprodutibilidade. Data exata: fim do semestre — a definir.

## A definir
- Datas exatas de entrega de P2 e P3 (cronograma oficial da turma no SIGAA, PSAE00263 - T01).
- (resolvido) Referência visual do dashboard — ver "Restrições / Referências visuais": estética techy/dark Plotly.
- Se a quebra de 2024 ganha uma visualização própria no dashboard (ex.: linha do tempo da janela linkada × teto 2024) ou fica restrita ao relatório.
- Cadência/forma da ingestão do módulo vivo (P2/P3): ingestão manual de novo CSV vs. automatizada; quais edições além de 2024 entram no MVP.
- Qual edição usar para demonstrar o módulo vivo já na entrega (ex.: ingerir 2024 RESULTADOS como prova de conceito de que sobrevive à quebra).
