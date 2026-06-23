# Dicionário da base analítica — ENEM 2022–2023 (US-03)

> Story: US-03 — Dicionário e decisões da base analítica (1 pt) [ÂNCORA] · depende de US-02.
> Escopo: registrar, em uma tabela auto-explicativa, as 14 colunas carregadas em `src/enem/carga.py`
> e as 4 colunas recodificadas em `src/enem/tratamento.py`, com origem rastreável ao dicionário
> INEP oficial (conferido nos `.xlsx` reais de 2022/2023, não de memória) e a justificativa de cada
> decisão de nulos/recodificação. Documento de DOCUMENTAÇÃO — nenhum código novo foi escrito aqui.

## Como ler esta tabela

- **Código original**: nome da coluna no CSV bruto do INEP (`COLUNAS_RELEVANTES` em `carga.py`).
- **Nome legível (base tratada)**: nome final na base analítica (`enem_2022_2023.parquet`).
  Para as 4 variáveis recodificadas, a coluna original é **descartada** após a recodificação
  (ver `tratamento.py::_recodificar`, linha que faz `drop(columns=[...])`) — só o nome legível
  sobrevive na base final.
- **Tipo**: dtype efetivo na base tratada.
- **Categorias / faixas (ordem)**: domínio de valores, na ordem em que aparecem na base (ordinal
  quando aplicável).
- **Regra de nulos**: o que acontece com ausência de valor.
- **Justificativa**: por que essa decisão e não outra.
- **Origem (rastreabilidade)**: arquivo/linha do dicionário INEP conferido ou módulo de código.

---

## 1. Identificação e marcador de edição

| Código original | Nome legível | Tipo | Categorias/faixas | Regra de nulos | Justificativa | Origem |
|---|---|---|---|---|---|---|
| `NU_INSCRICAO` | `NU_INSCRICAO` | `int64` | — (chave única do candidato) | Não há nulo (chave obrigatória do INEP). | Mantida tipada e não descartada para suportar joins/integridade futuros (US-01, comentário em `carga.py`). | `src/enem/carga.py::DTYPES` |
| `NU_ANO` | `NU_ANO` (bruto) → consolidado em `ano` após `tratamento.py` | `int16` (bruto) / `ano` final é `category` ordenada `[2022, 2023]` | `2022`, `2023` | Não há nulo (preenchido por edição). | Marcador de edição exigido pelo critério de aceite da US-02 (base unificada com coluna `ano`); recriado explicitamente em `tratar_edicao` em vez de confiar no `NU_ANO` bruto do CSV, garantindo consistência com o arquivo de origem lido. | `tratamento.py::tratar_edicao` (linha `df["ano"] = ...`) |

## 2. Notas (mantidas como vieram do INEP — sem recodificação)

| Código original | Nome legível | Tipo | Categorias/faixas | Regra de nulos | Justificativa | Origem |
|---|---|---|---|---|---|---|
| `NU_NOTA_CN` | `NU_NOTA_CN` | `float32` | nota 0–1000 (contínua) | `NaN` **mantido**. | Ausência de nota é legítima (candidato ausente/eliminado na área); imputar distorceria médias e distribuições usadas em P1, P2, P3, P5. ~24–28% de NaN por área, consistente entre 2022 e 2023 (verificado). | `tratamento.py`, bloco "DECISÕES DE TRATAMENTO DE NULOS"; rótulo conferido em `Dicionário_Microdados_Enem_2023.xlsx` (variável "Nota da prova de Ciências da Natureza") |
| `NU_NOTA_CH` | `NU_NOTA_CH` | `float32` | nota 0–1000 (contínua) | `NaN` mantido (mesma regra acima). | Idem. | idem |
| `NU_NOTA_LC` | `NU_NOTA_LC` | `float32` | nota 0–1000 (contínua) | `NaN` mantido (mesma regra acima). | Idem. | idem |
| `NU_NOTA_MT` | `NU_NOTA_MT` | `float32` | nota 0–1000 (contínua) | `NaN` mantido (mesma regra acima). | Idem. | idem |
| `NU_NOTA_REDACAO` | `NU_NOTA_REDACAO` | `float32` | nota 0–1000 (contínua); usada em US-08 (P5) para filtrar nota 1000 | `NaN` mantido (mesma regra acima). | Idem; é a variável-alvo de P5 (perfil de quem tira 1000). | idem |

> `float32` em vez de `float64`: decisão de eficiência de memória (RNF-02), não de tratamento de
> dados — registrada em `carga.py` (comentário no bloco `DTYPES`), não recodificação.

## 3. Variáveis socioeconômicas recodificadas (núcleo das perguntas P1, P4, P5)

| Código original | Nome legível | Tipo | Categorias/faixas (ordem) | Regra de nulos | Justificativa da recodificação | Origem |
|---|---|---|---|---|---|---|
| `Q006` | `faixa_renda` | `category` (ordenada) | `Sem renda` < `Ate 1 SM` < `1 a 2 SM` < `2 a 3 SM` < `3 a 4 SM` < `4 a 5 SM` < `5 a 6 SM` < `6 a 7 SM` < `7 a 8 SM` < `8 a 9 SM` < `9 a 10 SM` < `10 a 12 SM` < `12 a 15 SM` < `15 a 20 SM` < `Acima de 20 SM` | INEP não deixa em branco: quem não tem renda informada já recebe código `A` ("Nenhuma Renda") dentro do domínio. **0 NaN verificado nos CSVs.** Nenhuma imputação. | Os 17 códigos `A`–`Q` e a ordem ordinal são idênticos em 2022 e 2023, **mas as faixas em R$ mudaram** porque o salário mínimo de referência mudou: 2022 ancora em R$ 1.212,00 (confirmado no `Dicionário_Microdados_Enem_2022.xlsx`, var. Q006, código B = "Até R$ 1.212,00"); 2023 ancora em R$ 1.320,00 (confirmado no `Dicionário_Microdados_Enem_2023.xlsx`, código B = "Até R$ 1.320,00"). A posição ordinal de cada letra em **salários mínimos** é estável entre edições (ex.: a faixa `C`/`D` sempre corresponde a "1 a 2 SM" aproximadamente). Por isso `MAPA_Q006` recodifica pela faixa em SM, não pelo valor absoluto em R$ — evita misturar escalas monetárias diferentes ao concatenar 2022+2023. **Nota de comparabilidade (alerta para a dupla):** o mapeamento de blocos de letras→faixa de SM em `tratamento.py::MAPA_Q006` é uma aproximação conservadora por blocos ordinais (ex.: `C` e `D` colapsados em "1 a 2 SM"); não é uma conversão monetária exata letra-a-letra recalculada ano a ano — é a simplificação aceita para manter a categoria estável e legível entre edições. | `data/microdados_enem_2022/DICIONÁRIO/Dicionário_Microdados_Enem_2022.xlsx` (var. Q006) e `data/microdados_enem_2023/Dicionário_Microdados_Enem_2023.xlsx` (var. Q006), ambos conferidos diretamente; mapa em `tratamento.py::MAPA_Q006`/`ORDEM_Q006` |
| `Q001` | `escolaridade_pai` | `category` (ordenada) | `Nunca estudou` < `Fundamental I incompleto` < `Fundamental I completo` < `Fundamental II completo` < `Medio completo` < `Superior completo` < `Pos-graduacao` < `Nao sei` (fora da escala ordinal, ao final) | Códigos `A`–`H` idênticos nas duas edições; sem NaN nos CSVs — `H` ("Não sei") é o próprio "não informado" dentro do domínio do INEP. Nenhuma imputação. | Rótulos do INEP (`A` = "Nunca estudou", ..., `H` = "Não sei") foram simplificados para nomes curtos e estáveis, preservando a ordem ordinal real do dicionário INEP 2023: `A` Nunca estudou · `B` "Não completou a 4ª série/5º ano" · `C` "Completou a 4ª/5º, não completou a 8ª/9º" · `D` "Completou a 8ª/9º, não completou o Médio" · `E` "Completou o Médio, não completou a Faculdade" · `F` "Completou a Faculdade, não completou a Pós" · `G` "Completou a Pós-graduação" · `H` "Não sei". `H` é mantido como categoria não-ordenável ao final (não é "mais" nem "menos" escolaridade que `G`). | `Dicionário_Microdados_Enem_2023.xlsx` (var. Q001, conferido — mesmos códigos/rótulos em 2022); mapa em `tratamento.py::MAPA_ESCOLARIDADE`/`ORDEM_ESCOLARIDADE` |
| `Q002` | `escolaridade_mae` | `category` (ordenada) | mesma escala de `escolaridade_pai` | mesma regra de `Q001` (0 NaN; `H` = "Não sei" explícito). | Mesmo mapa `MAPA_ESCOLARIDADE`/`ORDEM_ESCOLARIDADE` reaplicado (Q002 é a versão materna da mesma pergunta no questionário INEP). | `Dicionário_Microdados_Enem_2023.xlsx` (var. Q002, mesmo domínio de Q001); `tratamento.py::MAPA_ESCOLARIDADE` |

## 4. Variáveis de contexto/escola (núcleo de P2)

| Código original | Nome legível | Tipo | Categorias/faixas (ordem) | Regra de nulos | Justificativa da recodificação | Origem |
|---|---|---|---|---|---|---|
| `TP_ESCOLA` | `tipo_escola` | `category` (não ordenada) | `Publica`, `Privada`, `Nao informado` | Código `1` do INEP é literalmente "Não Respondeu" — carrega os nulos de tipo de escola dentro do próprio domínio. **0 NaN verificado**, mas grande massa concentrada em `1`. Nenhuma imputação: o "não respondeu" é recodificado para `Nao informado` como categoria **explícita**, nunca dropada nem fundida com pública/privada. | Códigos `{1,2,3}` e rótulos (`1`="Não Respondeu", `2`="Pública", `3`="Privada") são **idênticos** nas duas edições — comparável direto, sem necessidade de normalização. | `Dicionário_Microdados_Enem_2023.xlsx` (var. TP_ESCOLA, código 1="Não Respondeu", 2="Pública", 3="Privada"); mapa em `tratamento.py::MAPA_TP_ESCOLA`/`ORDEM_TP_ESCOLA` |

> **⚠️ Alerta para a dupla e para a US-06 (P2)** — fato medido na base tratada (`enem_2022_2023.parquet`):
> `Nao informado` domina **70,1%** das linhas (70,5% em 2022; 69,8% em 2023), contra apenas 28,9%
> `Publica` e 1,0% `Privada`. O candidato médio do ENEM majoritariamente **não respondeu** essa
> pergunta do questionário — isso **não é um bug de tratamento**, é o próprio dado do INEP. Implicação
> direta para US-06/P2 (gap pública×privada): o `N` útil de comparação pública vs. privada cai para
> ~30% das linhas; qualquer gap calculado deve declarar esse `N` reduzido e a dupla deve decidir
> explicitamente se filtra `Nao informado` antes de comparar grupos ou se reporta as três categorias.
> Recomenda-se registrar esse `N` no relatório (US-11) como limitação, não escondê-lo.

## 5. Variáveis demográficas e geográficas (mantidas como vieram do INEP)

| Código original | Nome legível | Tipo | Categorias/faixas | Regra de nulos | Justificativa | Origem |
|---|---|---|---|---|---|---|
| `TP_COR_RACA` | `TP_COR_RACA` (sem recodificação na US-02; usada como está) | `category` | `0` Não declarado, `1` Branca, `2` Preta, `3` Parda, `4` Amarela, `5` Indígena, `6` Não dispõe da informação | Categoria `0` ("Não declarado") já é o "não informado" dentro do domínio INEP; nenhum NaN tratado nesta US. | Sem recodificação porque nenhuma pergunta P1–P5/EP-02b do escopo atual exige rótulo legível para esta variável ainda (consultar US-04/EDA se precisar mapear os códigos numéricos para rótulo de texto antes de plotar). | `Dicionário_Microdados_Enem_2023.xlsx` (var. TP_COR_RACA, conferido) |
| `TP_SEXO` | `TP_SEXO` (sem recodificação na US-02) | `category` | `M` Masculino, `F` Feminino | Sem nulo no domínio INEP (resposta obrigatória de identificação). | Sem recodificação — já vem como rótulo de letra legível (`M`/`F`), sem necessidade de mapa. | `Dicionário_Microdados_Enem_2023.xlsx` (var. TP_SEXO, conferido) |
| `SG_UF_PROVA` | `SG_UF_PROVA` (sem recodificação na US-02) | `category` | siglas de UF (ex.: `PB`, `SP`, `PE`...) | Sem nulo (local de aplicação da prova é sempre preenchido). | Sem recodificação — sigla de UF já é diretamente legível; o agrupamento por macrorregião (Nordeste vs. Sul/Sudeste, necessário para P3/US-07) é decisão de análise, não de tratamento, e fica para US-07. | `Dicionário_Microdados_Enem_2023.xlsx` (var. SG_UF_PROVA, conferido) |

---

## Resumo de cobertura

- **14 colunas brutas** carregadas em `carga.py::COLUNAS_RELEVANTES`/`DTYPES`: todas tabeladas
  (seções 1, 2, 4, 5 acima — `NU_INSCRICAO`, `NU_ANO`, 5 notas, `Q006`, `Q001`, `Q002`, `TP_ESCOLA`,
  `TP_COR_RACA`, `TP_SEXO`, `SG_UF_PROVA`).
- **4 colunas recodificadas** em `tratamento.py::_recodificar`: `faixa_renda`, `escolaridade_pai`,
  `escolaridade_mae`, `tipo_escola` — todas tabeladas com mapa, ordem e justificativa (seções 3 e 4).
- **1 coluna derivada de marcador**: `ano` — tabelada na seção 1.
- Rótulos originais conferidos diretamente nos `.xlsx` reais do INEP (2022 e 2023), não de memória,
  conforme exigido pelo RNF-04/critério de aceite da US-03.

## Pendências / observações para a dupla

1. O alerta de `tipo_escola` (70,1% "Não informado") é um achado factual do build, não uma decisão
   de tratamento errada — registrado aqui para a dupla decidir o filtro em US-06.
2. `TP_COR_RACA`, `TP_SEXO`, `SG_UF_PROVA` não foram recodificadas na US-02 (não havia necessidade
   até agora); se US-04/US-07/US-08 precisarem de rótulos de texto para raça (hoje em código numérico
   `0`–`6`) ou agrupamento de UF em macrorregião, isso é trabalho daquelas stories, não da US-03.
3. Nenhum erro factual foi encontrado em `carga.py`/`tratamento.py` durante a conferência contra os
   dicionários INEP reais — os comentários inline já estavam corretos (inclusive os valores exatos de
   R$ 1.212,00/R$ 1.320,00 citados no docstring de `tratamento.py`, confirmados nos `.xlsx`).
