"""Modelo preditivo interpretavel para o desempenho geral (P4) — US-09 + US-10.

Escopo: SO leitura do parquet tratado (US-02) + helpers de EDA (US-04). Define
o alvo e as variaveis preditoras do modelo (US-09), prepara X/y, treina uma
regressao linear e avalia R²/MAE no teste + ranking de variaveis por
contribuicao (US-10). NAO reprocessa CSV, NAO recodifica (isso e US-02).

------------------------------------------------------------------------------
DECISOES DE MODELAGEM (US-09 — ja fechada pela dupla, nao reabrir aqui)
------------------------------------------------------------------------------
ALVO (y) = media geral das 4 areas cognitivas (CN/CH/LC/MT), via
`eda.media_geral_notas` — a MESMA medida usada em P1-P3 (US-05..US-07). Por que
nao redacao: escala (0-1000 em criterios discretos) e distribuicao (mais
proxima de bimodal/discreta) diferem das 4 areas continuas, e a redacao tem
volume de NaN proprio; misturar as duas medidas no mesmo alvo enfraqueceria a
interpretabilidade do modelo e quebraria a comparabilidade com P1-P3, que ja
usam a media das 4 areas como "desempenho cognitivo geral". Por que media e
nao nota por area: um unico alvo interpretavel, com um unico conjunto de
coeficientes — o objetivo de P4 e o RANKING de drivers socioeconomicos, nao
prever cada area separadamente (isso multiplicaria o modelo por 4 sem ganho
de interpretabilidade para a pergunta de pesquisa).

VARIAVEIS PREDITORAS (X), todas categoricas SES ja recodificadas em US-02
(sem NaN, "Nao informado"/"Nao sei" como categoria explicita):
- `faixa_renda` (ordinal, ORDEM_Q006) — driver central de P1; renda e o eixo
  socioeconomico mais direto sobre acesso a recursos educacionais.
- `tipo_escola` (nominal, ORDEM_TP_ESCOLA) — driver central de P2; rede
  publica/privada captura qualidade/recursos da escola de origem.
- `escolaridade_pai`, `escolaridade_mae` (ordinais, ORDEM_ESCOLARIDADE) —
  capital cultural/educacional do nucleo familiar, fator SES classico e
  complementar a renda (educacao dos pais nem sempre acompanha renda 1:1).
- `TP_COR_RACA` (nominal, sem recodificacao previa — ver `eda.MAPA_COR_RACA`)
  — eixo de desigualdade racial, transversal a renda/escola no Brasil.
- `SG_UF_PROVA` recortada para `regiao` (nominal, ORDEM_REGIAO via
  `eda.MAPA_UF_REGIAO`) — driver central de P3; regiao captura desigualdade
  estrutural geografica (infraestrutura, oferta de vagas, IDH local) que UF
  isolada fragmentaria em 27 categorias esparsas demais para um ranking
  legivel de coeficientes.
- `ano` (ordinal, 2022/2023) — controla deslocamento temporal entre as duas
  edicoes (ex.: dificuldade da prova, contexto economico) sem ser o alvo da
  pergunta de pesquisa.

ENCODING: one-hot (`pd.get_dummies`, drop_first=True) para TODAS as
categoricas, inclusive as ordinais (faixa_renda, escolaridade_*). Decisao
deliberada para INTERPRETABILIDADE do ranking: coeficientes de regressao
linear sobre uma codificacao ordinal inteira (0,1,2,...) forcam um efeito
LINEAR constante entre categorias adjacentes — esconderiam, por exemplo, um
salto grande entre "Sem renda" e "Ate 1 SM" mas pequeno entre faixas altas.
One-hot com categoria de referencia (a primeira de cada ORDEM_*) permite ler
cada coeficiente como "quanto essa categoria muda a nota media frente a
referencia", sem impor essa premissa de linearidade — mais fiel ao objetivo
de RANKING de P4. O preco e mais colunas; aceitavel pois o objetivo nao e
parcimonia, e leitura de drivers.

ALVO SEM IMPUTACAO: linhas com NaN na media geral (candidato ausente/
eliminado em pelo menos uma das 4 areas) sao DROPADAS antes do treino —
nunca imputadas (decisao herdada de US-02/US-04). X (SES) nao tem NaN por
construcao da US-02.
"""

from __future__ import annotations

import argparse

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from .eda import MAPA_UF_REGIAO, ORDEM_REGIAO, carregar_base, media_geral_notas
from .tratamento import ORDEM_ESCOLARIDADE, ORDEM_Q006, ORDEM_TP_ESCOLA

COLUNAS_X = [
    "faixa_renda",
    "tipo_escola",
    "escolaridade_pai",
    "escolaridade_mae",
    "TP_COR_RACA",
    "regiao",
    "ano",
]

RANDOM_STATE_PADRAO = 42


def preparar_dados(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Monta X (one-hot) e y (media geral) a partir da base tratada.

    Dropa linhas com y NaN (nunca imputa — ver docstring do modulo). X nao tem
    NaN por construcao da US-02; `TP_COR_RACA` e tratado como categorico
    nominal e `regiao` e derivada de `SG_UF_PROVA` via `eda.MAPA_UF_REGIAO`,
    consistente com P3 (US-07).
    """
    df = base.copy()
    df["media_geral"] = media_geral_notas(df)
    df["regiao"] = df["SG_UF_PROVA"].astype(str).map(MAPA_UF_REGIAO)
    df["regiao"] = pd.Categorical(df["regiao"], categories=ORDEM_REGIAO, ordered=False)
    df["TP_COR_RACA"] = df["TP_COR_RACA"].astype(str)
    df["ano"] = df["ano"].astype(str)

    df = df.dropna(subset=["media_geral"])

    y = df["media_geral"]
    x_categorico = df[COLUNAS_X]
    x = pd.get_dummies(x_categorico, drop_first=True)
    return x, y


def treinar(
    x: pd.DataFrame, y: pd.Series, random_state: int = RANDOM_STATE_PADRAO
) -> tuple[LinearRegression, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Split treino/teste (80/20, `random_state` fixo) + treino da regressao."""
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x, y, test_size=0.2, random_state=random_state
    )
    modelo = LinearRegression()
    modelo.fit(x_treino, y_treino)
    return modelo, x_treino, y_treino, x_teste, y_teste


def avaliar(modelo: LinearRegression, x_teste: pd.DataFrame, y_teste: pd.Series) -> dict:
    """R² e MAE no conjunto de TESTE."""
    y_previsto = modelo.predict(x_teste)
    return {
        "r2": float(r2_score(y_teste, y_previsto)),
        "mae": float(mean_absolute_error(y_teste, y_previsto)),
        "n_teste": int(len(y_teste)),
    }


def ranking_variaveis(modelo: LinearRegression, x: pd.DataFrame) -> pd.DataFrame:
    """Agrega coeficientes one-hot por variavel ORIGINAL (soma do |coef| do grupo).

    Cada variavel categorica gerou varias colunas dummy (uma por categoria,
    exceto a referencia). Para um ranking por VARIAVEL (nao por categoria),
    agregamos pela soma dos valores absolutos dos coeficientes do grupo —
    aproxima o "alcance total" de cada variavel no modelo, mantendo a leitura
    por categoria disponivel na tabela detalhada.
    """
    coefs = pd.Series(modelo.coef_, index=x.columns)
    detalhado = coefs.sort_values(key=abs, ascending=False)

    grupo = coefs.index.to_series(index=coefs.index).apply(
        lambda col: next(c for c in COLUNAS_X if col.startswith(c + "_"))
    )
    agregado = (
        coefs.abs().groupby(grupo).sum().sort_values(ascending=False).rename("soma_abs_coef")
    )
    agregado = agregado.to_frame()
    agregado["n_categorias"] = grupo.value_counts()
    return agregado, detalhado


def _imprimir_conclusao(metricas: dict) -> None:
    print("\n--- CONCLUSAO P4 ---")
    print(
        f"R²={metricas['r2']:.3f}  MAE={metricas['mae']:.1f} pontos  "
        f"(N teste={metricas['n_teste']:,})."
    )
    print(
        "O modelo linear com fatores SES (renda, escola, escolaridade dos pais, "
        "raca/cor, regiao, ano) explica uma fracao MODESTA da variancia da nota "
        "media — esperado: desempenho no ENEM depende fortemente de fatores nao "
        "capturados aqui (trajetoria escolar individual, preparo especifico para "
        "a prova, fatores cognitivos/psicologicos), de modo que um R² baixo nao "
        "invalida o modelo, apenas delimita o que SES explica."
    )
    print(
        "Os coeficientes medem ASSOCIACAO, NAO CAUSALIDADE: renda, escola e "
        "regiao sao correlacionadas entre si (a mesma limitacao registrada em "
        "P1-P3), e o modelo nao isola efeito causal de nenhuma variavel."
    )


def _imprimir_resumo(base: pd.DataFrame, random_state: int) -> None:
    print("\n--- VALIDACAO US-09/US-10 (P4) ---")
    print("linhas totais (antes do dropna de y):", f"{len(base):,}")

    x, y = preparar_dados(base)
    print("linhas apos dropar y NaN:", f"{len(y):,}")
    print("colunas de X (one-hot):", x.shape[1])

    modelo, x_treino, y_treino, x_teste, y_teste = treinar(x, y, random_state=random_state)
    print(f"\nsplit: treino={len(y_treino):,}  teste={len(y_teste):,}  random_state={random_state}")

    metricas = avaliar(modelo, x_teste, y_teste)
    print(f"\nR² (teste) = {metricas['r2']:.4f}")
    print(f"MAE (teste) = {metricas['mae']:.2f} pontos")

    agregado, detalhado = ranking_variaveis(modelo, x)
    print("\nranking de variaveis por contribuicao (soma |coef| das categorias do grupo):")
    print(agregado.round(2).to_string())

    print("\ndetalhe por categoria (top 15 |coef|):")
    print(detalhado.head(15).round(2).to_string())

    _imprimir_conclusao(metricas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="US-09/US-10: modelo P4 — regressao linear interpretavel"
    )
    parser.add_argument(
        "--nrows", type=int, default=None, help="amostra para teste rapido (default: base inteira)"
    )
    parser.add_argument(
        "--random-state", type=int, default=RANDOM_STATE_PADRAO, help="seed do split treino/teste"
    )
    args = parser.parse_args()

    base = carregar_base(nrows=args.nrows)
    _imprimir_resumo(base, random_state=args.random_state)
