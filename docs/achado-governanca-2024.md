# Achado de governança: a quebra de linkage dos microdados ENEM 2024

> **Natureza deste documento.** Registro factual de uma mudança estrutural na
> base pública do ENEM a partir de 2024, ancorado no documento oficial do INEP.
> Não é um bug a corrigir — é um **achado de governança de dados** que define o
> teto temporal da análise (2023). A classificação de quais perguntas de
> pesquisa morrem e quais sobrevivem é tratada na US-18, não aqui.

**Fonte primária (US-17).** Todas as afirmações factuais abaixo são ancoráveis a:

> INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA.
> *Microdados do Enem 2024 — LEIA-ME.* Brasília: Inep, junho de 2025.
> Arquivo: `data/microdados_enem_2024/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2024.pdf`.

A referência abreviada `LEIA-ME, p.N` aparece ao lado de cada afirmação-chave.

---

## 1. Contexto: 2009–2023 tinha base única por participante

O ENEM, na sua forma reformulada em 2009 (quatro áreas do conhecimento, 180
questões objetivas + redação), passou a ser a principal via de acesso ao ensino
superior público (LEIA-ME, p.5). Além das provas, cada participante responde a um
questionário sobre nível socioeconômico, família, educação e trabalho — em 2024,
composto por 23 questões (LEIA-ME, p.6).

Nas edições de 2009 a 2023, as informações de perfil socioeconômico (o
questionário) e o desempenho (notas/proficiências) do **mesmo indivíduo**
conviviam numa estrutura de microdados por participante que permitia parear
diretamente perfil ↔ nota. É essa propriedade — o pareamento individual — que a
edição 2024 rompe.

> Observação factual: o LEIA-ME de 2024 descreve o histórico do exame (p.4–6),
> mas **não** detalha a estrutura interna das bases das edições anteriores a
> 2024. A afirmação de que 2009–2023 permitia o pareamento individual deriva da
> estrutura conhecida dessas bases (usada no pipeline 2022–2023 deste projeto),
> não de uma frase explícita do documento de 2024.

---

## 2. O que mudou em 2024: duas bases sem chave comum

A partir da edição 2024 o INEP **dividiu a base de microdados do ENEM em duas**
(LEIA-ME, p.7):

| Base | Conteúdo | Âncora |
| --- | --- | --- |
| `PARTICIPANTES_2024.csv` | Informações gerais dos participantes e o **questionário socioeconômico** respondido no ato da inscrição. | LEIA-ME, p.6 (§3) e p.10 (Quadro 2) |
| `RESULTADOS_2024.csv` | **Escola** de conclusão do ensino médio, provas, gabaritos e **proficiências** (notas). | LEIA-ME, p.7 (§1) e p.10 (Quadro 2) |
| `ITENS_PROVA_2024.csv` | Informações gerais sobre os itens das provas (posição, habilidade, gabarito, parâmetros psicométricos). | LEIA-ME, p.8 e p.10 (Quadro 2) |

O documento afirma textualmente:

> "A base de dados dos microdados do ENEM foi dividida em duas:
> PARTICIPANTES_2024 e RESULTADOS_2024. (...) **Uma vez que as duas bases não
> possuem chave de ligação em comum**, a informação da escola não possibilitará
> a identificação indevida dos participantes do exame, em fiel observância ao
> que estabelece a Lei Geral de Proteção de Dados Pessoais (LGPD)."
> — LEIA-ME, p.7.

A ausência de chave de ligação é, portanto, **deliberada e declarada pelo
próprio INEP**, não um defeito de empacotamento.

---

## 3. Por que isso quebra o pareamento perfil ↔ nota

O perfil socioeconômico do indivíduo vive **só** em `PARTICIPANTES_2024`; a nota
do indivíduo vive **só** em `RESULTADOS_2024` (LEIA-ME, p.6–7). Sem uma chave
comum entre as duas bases (LEIA-ME, p.7), não há como afirmar qual linha de
`RESULTADOS_2024` corresponde a qual linha de `PARTICIPANTES_2024`.

Consequência factual: **não é possível associar, no nível do indivíduo, a renda
declarada (ou qualquer variável do questionário) à nota obtida.** Qualquer
junção entre as duas bases seria arbitrária. Análises que dependem desse
pareamento individual (perfil socioeconômico × desempenho do mesmo participante)
deixam de ser respondíveis com os microdados públicos de 2024.

> O LEIA-ME não usa as expressões "pareamento" ou "perfil × nota"; descreve
> apenas as duas bases e a ausência de chave (p.7). A implicação para o
> pareamento individual é uma leitura direta dessa ausência de chave, não uma
> citação literal.

---

## 4. Base legal declarada pelo INEP (LGPD)

O INEP atribui a separação à **proteção de dados pessoais**. A base legal aparece
explícita no documento:

- O LEIA-ME cita a **Lei Geral de Proteção de Dados (LGPD), Lei nº 13.709, de 14
  de agosto de 2018**, afirmando que, em razão de sua vigência, "o INEP viu-se
  obrigado a realizar mudanças no modelo de microdados" do ENEM (LEIA-ME, p.4).
- O documento explica que o conceito de dado anonimizado do art. 5º, III da LGPD
  não define objetivamente o que são "esforços razoáveis" de reidentificação;
  por isso "o INEP optou pela cautela", adotando um modelo simplificado de
  microdados usado desde a edição 2020 (LEIA-ME, p.4).
- A separação das duas bases é justificada como sendo "em fiel observância ao que
  estabelece a Lei Geral de Proteção de Dados Pessoais (LGPD)": a falta de chave
  comum impede que a informação da escola (reintroduzida em 2024) seja usada para
  identificação indevida do participante (LEIA-ME, p.7).

> Nota factual: o documento **não** cita número de resolução nem manifestação
> específica da ANPD; atribui a mudança à LGPD (Lei nº 13.709/2018) e à cautela
> do próprio INEP (LEIA-ME, p.4 e p.7). Qualquer menção à ANPD além disso não
> consta no LEIA-ME.

---

## 5. Gancho para a US-18 (não resolvido aqui)

A quebra de linkage não apaga 2024 por inteiro — ela apaga **um eixo** (o
pareamento individual perfil ↔ nota) e preserva outros. `RESULTADOS_2024` ainda
traz escola de conclusão e proficiências na mesma base (LEIA-ME, p.7), o que
mantém vivos os eixos que não dependem do questionário socioeconômico.

A classificação formal de **quais perguntas de pesquisa morrem e quais
sobrevivem** em 2024+ (P1/P4/P5 vs. P2/P3, raça×nota, sexo×nota) e a justificativa
escrita do **teto temporal 2023** são objeto da **US-18** e não são resolvidas
neste documento. Ressalvas adicionais que o pesquisador deve conhecer ao tocar
em 2024:

- A variável `NU_IDADE` foi substituída por `TP_FAIXA_ETARIA` em
  `PARTICIPANTES_2024` (LEIA-ME, p.7).
- Foram removidos município de nascimento/residência e os pedidos de atendimento
  especializado (LEIA-ME, p.7).
- O código da escola foi obtido do Censo Escolar 2024 via CPF e mascarado quando
  a instituição teve menos de 10 participantes; o INEP **não recomenda** usar
  esses resultados para rankings de escolas (LEIA-ME, p.7–8).
