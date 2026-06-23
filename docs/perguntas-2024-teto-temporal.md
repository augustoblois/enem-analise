# Perguntas que morrem vs. sobrevivem em 2024+ e o teto temporal 2023

> **Natureza deste documento (US-18).** Aplica o achado factual da US-17
> (`docs/achado-governanca-2024.md`) às perguntas de pesquisa do projeto.
> Classifica cada pergunta como **MORRE** ou **SOBREVIVE** na edição 2024+ dos
> microdados, justifica por escrito o **teto temporal 2023** como consequência
> direta da quebra, e conecta o resultado às LIMITAÇÕES do relatório (US-11) e ao
> escopo do MÓDULO VIVO (EP-07). Não ingere dados de 2024 nem escreve código.

**Âncora factual.** Todas as afirmações sobre a estrutura de 2024 derivam do
achado da US-17, que por sua vez ancora no documento oficial do INEP
(*Microdados do Enem 2024 — LEIA-ME*, jun/2025). As seções citadas abaixo
(`US-17 §N`) referem-se a `docs/achado-governanca-2024.md`.

---

## 1. O critério único de classificação

A quebra de 2024 separou os microdados em **duas bases sem chave de ligação
comum** (US-17 §2, citando LEIA-ME p.7):

- `PARTICIPANTES_2024` — informações gerais + **questionário socioeconômico**
  (renda, escolaridade dos pais, etc.) (US-17 §2).
- `RESULTADOS_2024` — **escola** de conclusão, provas, gabaritos e
  **proficiências (notas)** (US-17 §2).

Como não há chave comum entre as duas bases, **não é possível associar, no nível
do indivíduo, nenhuma variável do questionário (PARTICIPANTES) à nota
(RESULTADOS)** (US-17 §3). Qualquer junção seria arbitrária.

Disso decorre o critério único e mecânico de classificação:

> **A pergunta SOBREVIVE se — e somente se — as duas pontas que ela cruza
> (a variável de corte E a nota) vivem na MESMA base em 2024.**
> Como a nota vive em `RESULTADOS_2024`, a pergunta sobrevive apenas quando a
> variável de corte também está em `RESULTADOS_2024`. Se a variável de corte
> está em `PARTICIPANTES_2024`, o cruzamento exige parear as duas bases — e isso
> a quebra de linkage tornou impossível: a pergunta MORRE.

---

## 2. Tabela de classificação

| Pergunta | Cruza | Morre / Sobrevive | Razão (ancorada na quebra de linkage) | Onde o dado vive em 2024 |
| --- | --- | --- | --- | --- |
| **P1** — renda × nota | renda (`Q006`) × nota | **MORRE** | Renda é variável do questionário socioeconômico → só em `PARTICIPANTES`. A nota só em `RESULTADOS`. Sem chave comum, não há como parear renda↔nota do mesmo indivíduo (US-17 §3). | renda em PARTICIPANTES; nota em RESULTADOS → **bases separadas** |
| **P4** — preditores SES da nota | conjunto SES (renda, escolaridade dos pais, etc.) × nota | **MORRE** | O modelo preditivo usa preditores que são, em sua maioria, variáveis do questionário (PARTICIPANTES) tendo a nota (RESULTADOS) como alvo. O pareamento preditor↔alvo no indivíduo é exatamente o que a quebra impede (US-17 §3). | preditores SES em PARTICIPANTES; alvo (nota) em RESULTADOS → **bases separadas** |
| **P5** — perfil SES das notas 1000 | nota 1000 → perfil SES (renda/escola privada/escolaridade dos pais) | **MORRE** | Filtra-se a nota (RESULTADOS) e depois lê-se o perfil socioeconômico (PARTICIPANTES) dos mesmos indivíduos. Sem chave comum, não se sabe qual linha de PARTICIPANTES corresponde a cada nota 1000 (US-17 §3). | nota em RESULTADOS; perfil SES em PARTICIPANTES → **bases separadas** |
| **P2** — escola pública × privada × nota | tipo de escola × nota | **SOBREVIVE** | A escola de conclusão do ensino médio voltou para `RESULTADOS` em 2024, **na mesma base** que as proficiências (US-17 §2 e §5). Cruzar tipo de escola × nota não atravessa a fronteira entre as duas bases. | **ambos em RESULTADOS** (mesma base) |
| **P3** — disparidade regional × nota | UF/região × nota | **SOBREVIVE** | A UF/local de prova acompanha as proficiências em `RESULTADOS` (US-17 §5: os eixos que não dependem do questionário permanecem vivos). Cruzar região × nota não atravessa a fronteira. | **ambos em RESULTADOS** (mesma base) |
| **raça × nota** | `TP_COR_RACA` × nota | **MORRE** *(inferido — ver nota de incerteza)* | Cor/raça é item do questionário do participante. Em 2024 o questionário inteiro está em `PARTICIPANTES`, separado da nota (RESULTADOS). Cruzar raça × nota exigiria parear as duas bases → impossível sem chave (US-17 §2–§3). | raça em PARTICIPANTES; nota em RESULTADOS → **bases separadas** *(a posição exata de `TP_COR_RACA` não é citada literalmente na US-17 — ver §2.1)* |
| **sexo × nota** | `TP_SEXO` × nota | **MORRE** *(inferido — ver nota de incerteza)* | Mesmo raciocínio: sexo é atributo declarado pelo participante, associado ao bloco de PARTICIPANTES, separado da nota em RESULTADOS. O cruzamento atravessaria a fronteira sem chave (US-17 §2–§3). | sexo em PARTICIPANTES; nota em RESULTADOS → **bases separadas** *(posição exata não citada literalmente — ver §2.1)* |

### 2.1 Nota de incerteza sobre raça e sexo (declarada, não mascarada)

O documento da US-17 confirma textualmente apenas que (a) `PARTICIPANTES` contém
"informações gerais dos participantes e o questionário socioeconômico" e (b)
`RESULTADOS` contém escola, provas e proficiências (US-17 §2). Ele **não cita
nominalmente** em qual das duas bases ficam `TP_COR_RACA` e `TP_SEXO`.

A classificação "MORRE" para raça×nota e sexo×nota é, portanto, uma **inferência
fundamentada**, não uma citação literal: raça e sexo são atributos do
participante / itens declarados na inscrição, naturalmente associados ao bloco de
informações do participante (PARTICIPANTES), e não às proficiências (RESULTADOS).
Há um indício adicional na mesma linha: a US-17 §5 registra que `NU_IDADE` (idade
exata, atributo do participante) foi substituída por `TP_FAIXA_ETARIA` em
`PARTICIPANTES` — confirmando que os atributos demográficos do indivíduo vivem do
lado de PARTICIPANTES.

**Ressalva honesta:** caso `TP_COR_RACA` e/ou `TP_SEXO` estejam, na verdade,
replicados em `RESULTADOS_2024` (o que o LEIA-ME poderia esclarecer e a US-17 não
verificou item a item), esses dois cruzamentos passariam a SOBREVIVER pela mesma
lógica de P2/P3. Enquanto essa verificação direta no LEIA-ME não for feita,
mantém-se a classificação "MORRE" como a leitura mais provável, com a incerteza
explicitada.

---

## 3. Justificativa escrita do teto temporal 2023

O **núcleo socioeconômico ↔ nota** do projeto — P1 (renda×nota), P4 (preditores
SES) e P5 (perfil SES das notas 1000) — depende inteiramente de parear, no mesmo
indivíduo, uma variável do questionário com a nota obtida. Esse pareamento existe
nos microdados de 2009 a 2023, quando perfil e desempenho conviviam numa estrutura
única por participante (US-17 §1). A edição 2024 rompe exatamente essa propriedade
ao separar as bases sem chave comum (US-17 §2–§3).

Consequência direta: **2023 é a última edição em que o núcleo P1/P4/P5 é
respondível com os microdados públicos.** O teto temporal 2023 não é uma escolha
de escopo arbitrária — é o ponto onde a base deixa de suportar a pergunta central
da tese. Por isso:

- a **tese recorta a janela 2009–2023** (último ano com linkage individual SES↔nota);
- o **pipeline analítico deste projeto usa 2022–2023** (as duas edições mais
  recentes ainda dentro do teto, comparáveis entre si).

Edições de 2024 em diante **não entram no núcleo SES** porque não há resposta
possível para P1/P4/P5 nelas — não por falta de dados de nota, mas por
impossibilidade estrutural de associá-los ao perfil socioeconômico (US-17 §3).

---

## 4. Conexões com o restante da governança

### 4.1 Seção de LIMITAÇÕES do relatório (insumo para US-11)

Este documento é insumo direto da seção de limitações de `US-11` (relatório
técnico). Pontos a transportar para lá:

- **Teto temporal 2023 como limitação assumida e justificada**, ao lado das
  outras duas já previstas (R² baixo do modelo P4; não-causalidade de P3).
- A limitação não é "dados antigos", e sim **uma fronteira de respondibilidade**:
  o eixo central (SES↔nota) é estruturalmente irrespondível a partir de 2024
  (US-17 §3), enquanto os eixos escola×nota e região×nota seguem respondíveis.
- A incerteza de §2.1 (posição de raça/sexo) deve ser reportada como ressalva,
  não omitida.

### 4.2 Escopo do MÓDULO VIVO (EP-07)

A classificação acima **define o escopo do módulo vivo**: só sobrevivem à quebra,
para ingestão de edições novas, **P2 (escola×nota) e P3 (região×nota), via
`RESULTADOS`** — exatamente porque ambas as pontas de cada cruzamento moram na
mesma base em 2024. É por isso que o EP-07:

- ingere apenas o `RESULTADOS` de cada edição nova (escola/UF + notas), sem tocar
  o questionário;
- **não reprocessa o núcleo SES** (P1/P4/P5), que está congelado em 2022–2023 por
  ser irrespondível em 2024+;
- usa **RESULTADOS_2024 como prova de conceito** (US-23): a única parte de 2024
  que o projeto consegue, legitimamente, comparar lado a lado com 2022–2023.

Em uma frase: **a quebra de linkage mata o núcleo SES a partir de 2024 e poupa os
eixos de RESULTADOS — e é essa poupança que o módulo vivo explora.**
