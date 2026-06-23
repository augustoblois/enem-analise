"""Analise exploratoria inicial da base tratada 2022+2023 (US-04).

Escopo: SOMENTE leitura do parquet ja tratado (US-02, `tratamento.CAMINHO_PARQUET`)
e producao de evidencia exploratoria — figuras PNG em `docs/figuras/` e um resumo
textual no stdout. NAO reprocessa CSV bruto, NAO recodifica nada (isso e US-02),
NAO faz modelagem.

------------------------------------------------------------------------------
DECISOES DE EDA (insumo para o relatorio US-11)
------------------------------------------------------------------------------
- Notas: ~24-28% de NaN e LEGITIMO (candidato ausente/eliminado, ver tratamento.py).
  Para describe/histograma/boxplot/skewness usamos `.dropna()` apenas no calculo
  pontual, nunca preenchendo o NaN — e reportamos o % de ausencia por nota/ano
  para que o leitor veja a base do calculo.
- `tipo_escola`: 70,1% "Nao informado" (fato do INEP, nao bug). Qualquer comparacao
  Publica x Privada reporta o N reduzido (~30% da base) e mostra as 3 categorias
  na tabela de frequencia, decidindo explicitamente se filtra ou nao em cada grafico.
- `faixa_renda`/`escolaridade_*` sao ORDINAIS — a ordem das categorias (`cat.categories`)
  e usada diretamente nos eixos dos graficos, nunca ordem alfabetica.
- `TP_COR_RACA` nao tem rotulo na base tratada (US-02 nao recodificou); aplicamos
  aqui um mapa de rotulo LOCAL (`MAPA_COR_RACA`) so para leitura dos graficos,
  sem alterar a base.
- Macrorregiao por UF e derivada aqui (`MAPA_UF_REGIAO`), decisao de analise (US-04),
  nao de tratamento — consistente com a nota do dicionario (US-03, secao 5).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from .carga import RAIZ_PROJETO
from .tratamento import CAMINHO_PARQUET, ORDEM_ESCOLARIDADE, ORDEM_Q006, ORDEM_TP_ESCOLA

DIR_FIGURAS = RAIZ_PROJETO / "docs" / "figuras"

NOTAS = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
ROTULO_NOTA = {
    "NU_NOTA_CN": "Ciencias da Natureza",
    "NU_NOTA_CH": "Ciencias Humanas",
    "NU_NOTA_LC": "Linguagens e Codigos",
    "NU_NOTA_MT": "Matematica",
    "NU_NOTA_REDACAO": "Redacao",
}

MAPA_COR_RACA: dict[str, str] = {
    "0": "Nao declarado",
    "1": "Branca",
    "2": "Preta",
    "3": "Parda",
    "4": "Amarela",
    "5": "Indigena",
    "6": "Nao dispoe",
}

# Macrorregiao por UF — decisao de analise (US-04), nao do tratamento (US-02/US-03).
MAPA_UF_REGIAO: dict[str, str] = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte",
    "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}
ORDEM_REGIAO = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def carregar_base(nrows: int | None = None) -> pd.DataFrame:
    """Le a base tratada (parquet da US-02). `nrows` so para teste rapido."""
    if not CAMINHO_PARQUET.exists():
        raise FileNotFoundError(f"Parquet tratado nao encontrado: {CAMINHO_PARQUET}")
    base = pd.read_parquet(CAMINHO_PARQUET)
    if nrows is not None:
        base = base.head(nrows)
    return base


def _ano_str(base: pd.DataFrame) -> pd.Series:
    """Coluna `ano` como string, robusta a dtype (category ou int)."""
    return base["ano"].astype(str)


def plotar_distribuicoes_notas(base: pd.DataFrame) -> Path:
    """Histograma + boxplot por area (5 notas + redacao). Salva 1 PNG combinado."""
    fig, eixos = plt.subplots(2, 5, figsize=(22, 8))
    for col, eixo_hist, eixo_box in zip(NOTAS, eixos[0], eixos[1]):
        valores = base[col].dropna()
        eixo_hist.hist(valores, bins=50, color="#4472c4", edgecolor="none")
        eixo_hist.set_title(ROTULO_NOTA[col])
        eixo_hist.set_xlabel("nota")
        eixo_box.boxplot(valores, vert=True)
        eixo_box.set_xticklabels([""])
    fig.suptitle("Distribuicao das notas por area — ENEM 2022+2023")
    fig.tight_layout()
    destino = DIR_FIGURAS / "distribuicao_notas.png"
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    return destino


def resumo_ses(base: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tabelas de frequencia/proporcao para faixa_renda, tipo_escola e regiao."""
    regiao = base["SG_UF_PROVA"].astype(str).map(MAPA_UF_REGIAO)
    regiao = pd.Categorical(regiao, categories=ORDEM_REGIAO, ordered=False)

    tabelas = {
        "faixa_renda": base["faixa_renda"].cat.set_categories(ORDEM_Q006).value_counts().reindex(ORDEM_Q006),
        "tipo_escola": base["tipo_escola"].cat.set_categories(ORDEM_TP_ESCOLA).value_counts().reindex(ORDEM_TP_ESCOLA),
        "regiao": pd.Series(regiao).value_counts().reindex(ORDEM_REGIAO),
    }
    for nome, contagem in tabelas.items():
        proporcao = (contagem / contagem.sum() * 100).round(1)
        tabelas[nome] = pd.DataFrame({"n": contagem, "%": proporcao})
    return tabelas


def plotar_resumo_ses(tabelas: dict[str, pd.DataFrame]) -> Path:
    """Grafico de barras (3 paineis) para faixa_renda, tipo_escola e regiao."""
    fig, eixos = plt.subplots(1, 3, figsize=(18, 5))
    for eixo, (nome, tabela) in zip(eixos, tabelas.items()):
        eixo.bar(tabela.index.astype(str), tabela["n"], color="#70ad47")
        eixo.set_title(nome)
        eixo.tick_params(axis="x", rotation=60)
    fig.suptitle("Perfil socioeconomico — ENEM 2022+2023")
    fig.tight_layout()
    destino = DIR_FIGURAS / "resumo_socioeconomico.png"
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    return destino


def media_geral_notas(base: pd.DataFrame) -> pd.Series:
    """Media simples das 5 areas (sem redacao) por linha, ignorando NaN por linha."""
    return base[["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT"]].mean(axis=1, skipna=True)


def plotar_comparacao_grupos(base: pd.DataFrame) -> Path:
    """Boxplot da media geral por tipo_escola e por faixa_renda."""
    media = media_geral_notas(base)
    df = pd.DataFrame({"media": media, "tipo_escola": base["tipo_escola"], "faixa_renda": base["faixa_renda"]})
    df = df.dropna(subset=["media"])

    fig, (eixo_escola, eixo_renda) = plt.subplots(1, 2, figsize=(16, 6))

    grupos_escola = [df.loc[df["tipo_escola"] == cat, "media"] for cat in ORDEM_TP_ESCOLA]
    eixo_escola.boxplot(grupos_escola, tick_labels=ORDEM_TP_ESCOLA)
    eixo_escola.set_title("Media geral (CN/CH/LC/MT) por tipo de escola")
    eixo_escola.tick_params(axis="x", rotation=20)

    grupos_renda = [df.loc[df["faixa_renda"] == cat, "media"] for cat in ORDEM_Q006]
    eixo_renda.boxplot(grupos_renda, tick_labels=ORDEM_Q006)
    eixo_renda.set_title("Media geral (CN/CH/LC/MT) por faixa de renda")
    eixo_renda.tick_params(axis="x", rotation=75)

    fig.tight_layout()
    destino = DIR_FIGURAS / "comparacao_grupos.png"
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    return destino


def percentual_nan_por_ano(base: pd.DataFrame) -> pd.DataFrame:
    """% de NaN por nota, quebrado por ano (evidencia do criterio de nulos residuais)."""
    anos = _ano_str(base)
    linhas = {}
    for ano in sorted(anos.unique()):
        subset = base.loc[anos == ano, NOTAS]
        linhas[ano] = (subset.isna().mean() * 100).round(1)
    return pd.DataFrame(linhas)


def skewness_notas(base: pd.DataFrame) -> pd.Series:
    """Assimetria (Fisher-Pearson) por nota, calculada sobre valores nao-nulos."""
    valores = {}
    for col in NOTAS:
        amostra = base[col].dropna().to_numpy()
        valores[col] = float(stats.skew(amostra))
    return pd.Series(valores)


def outliers_iqr(base: pd.DataFrame) -> pd.Series:
    """Contagem de outliers por nota via regra do IQR (1.5x), sobre valores nao-nulos."""
    contagens = {}
    for col in NOTAS:
        valores = base[col].dropna()
        q1, q3 = valores.quantile([0.25, 0.75])
        iqr = q3 - q1
        baixo, alto = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        contagens[col] = int(((valores < baixo) | (valores > alto)).sum())
    return pd.Series(contagens)


def _imprimir_observacoes(base: pd.DataFrame, skew: pd.Series, outliers: pd.Series, nan_ano: pd.DataFrame) -> None:
    print("\n--- OBSERVACOES ANOTADAS (US-04) ---")
    print(
        "Nulos residuais: cada nota mantem ~24-28% de NaN, consistente entre 2022 e 2023 "
        "(ver tabela acima) — e o candidato ausente/eliminado, NAO um erro de tratamento; "
        "nao foi imputado (decisao herdada da US-02)."
    )
    for col in NOTAS:
        s = skew[col]
        forma = "aprox. simetrica" if abs(s) < 0.5 else ("assimetria positiva (cauda a direita)" if s > 0 else "assimetria negativa (cauda a esquerda)")
        print(f"  {ROTULO_NOTA[col]:<22} skew={s:+.3f} ({forma}); outliers IQR={outliers[col]:,}")
    print(
        "Outliers via regra do IQR sao esperados nas extremidades (notas 0 de eliminados que "
        "ainda tem valor registrado, ou notas muito altas/baixas legitimas) — nao foram removidos."
    )
    n_naoinformado = int((base["tipo_escola"] == "Nao informado").sum())
    pct_naoinformado = round(n_naoinformado / len(base) * 100, 1)
    print(
        f"tipo_escola: {pct_naoinformado}% das linhas sao 'Nao informado' (N util Publica/Privada "
        f"= {100 - pct_naoinformado:.1f}% da base) — fato do INEP, ver docs/dicionario-base.md."
    )


def _imprimir_resumo(base: pd.DataFrame) -> None:
    print("\n--- VALIDACAO US-04 ---")
    print("linhas totais:", f"{len(base):,}")

    print("\ndescribe() das notas (calculado sobre valores nao-nulos):")
    print(base[NOTAS].describe().round(2).to_string())

    nan_ano = percentual_nan_por_ano(base)
    print("\n% de NaN por nota, por ano:")
    print(nan_ano.to_string())

    skew = skewness_notas(base)
    outliers = outliers_iqr(base)

    print("\ntabelas de frequencia socioeconomica:")
    tabelas = resumo_ses(base)
    for nome, tabela in tabelas.items():
        print(f"\n{nome}:")
        print(tabela.to_string())

    print("\nmedia geral (CN/CH/LC/MT) por tipo_escola:")
    media = media_geral_notas(base)
    print(media.groupby(base["tipo_escola"], observed=True).describe()[["count", "mean", "std"]].round(2).to_string())

    print("\nmedia geral (CN/CH/LC/MT) por faixa_renda:")
    print(media.groupby(base["faixa_renda"], observed=True).describe()[["count", "mean", "std"]].round(2).to_string())

    _imprimir_observacoes(base, skew, outliers, nan_ano)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="US-04: EDA inicial da base tratada 2022+2023")
    parser.add_argument("--nrows", type=int, default=None,
                        help="amostra para teste rapido (default: base inteira)")
    args = parser.parse_args()

    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)

    base = carregar_base(nrows=args.nrows)
    _imprimir_resumo(base)

    fig1 = plotar_distribuicoes_notas(base)
    tabelas = resumo_ses(base)
    fig2 = plotar_resumo_ses(tabelas)
    fig3 = plotar_comparacao_grupos(base)

    print("\nfiguras geradas:")
    for fig in (fig1, fig2, fig3):
        print(f"  {fig}")
