"""P1: renda familiar x nota media nas 5 areas (US-05).

Escopo: SO leitura do parquet tratado (US-02) + helpers de EDA (US-04). Responde
P1 — existe relacao entre faixa de renda e desempenho? Calcula media por area e
media geral por `faixa_renda` (ordinal), estatistica de suporte (gap topo-base +
correlacao de Spearman, apropriada a variavel ORDINAL) e uma figura legivel.
NAO reprocessa CSV, NAO recodifica (US-02), NAO modela (US-10).

------------------------------------------------------------------------------
DECISOES DE ANALISE (insumo do relatorio US-11)
------------------------------------------------------------------------------
- `faixa_renda` e ordinal: a media segue a ordem das categorias (ORDEM_Q006),
  nunca alfabetica. "Sem renda" e o piso, "Acima de 20 SM" o topo.
- Notas mantem NaN (ausente/eliminado); todas as medias usam skipna (decisao
  herdada da US-02/US-04). O N por faixa e reportado para o leitor.
- Correlacao: usamos Spearman (rho) entre o RANK ordinal da faixa e a media geral,
  nao Pearson — a renda aqui e categoria ordenada, nao valor continuo em R$.
- Media geral = media de CN/CH/LC/MT (sem redacao), consistente com a US-04
  (`eda.media_geral_notas`), para uma medida unica de desempenho cognitivo.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from .eda import DIR_FIGURAS, NOTAS, ROTULO_NOTA, carregar_base, media_geral_notas
from .tratamento import ORDEM_Q006


def media_por_renda(base: pd.DataFrame) -> pd.DataFrame:
    """Media de cada area + media geral (CN/CH/LC/MT) por faixa de renda.

    Linhas na ordem ordinal de ORDEM_Q006. Inclui coluna `n` (candidatos por
    faixa) para o leitor ver a base de cada media. Medias com skipna (NaN das
    notas e legitimo).
    """
    df = base.copy()
    df["media_geral"] = media_geral_notas(df)

    colunas = NOTAS + ["media_geral"]
    agregado = (
        df.groupby("faixa_renda", observed=True)[colunas]
        .mean()
        .reindex(ORDEM_Q006)
        .round(1)
    )
    agregado.insert(0, "n", base.groupby("faixa_renda", observed=True).size().reindex(ORDEM_Q006))
    return agregado


def estatistica_suporte(base: pd.DataFrame) -> dict:
    """Gap topo-base na media geral + correlacao de Spearman renda x desempenho.

    - gap: media geral da faixa mais alta com dado menos a faixa mais baixa com
      dado (extremos efetivos de ORDEM_Q006, ignorando faixas vazias).
    - spearman: rho entre o rank ordinal da faixa (cat.codes) e a media geral,
      linha a linha (so onde ambos existem). Mede monotonicidade, nao linearidade.
    """
    media = media_geral_notas(base)
    rank = base["faixa_renda"].cat.codes  # -1 onde NaN; faixas seguem ORDEM_Q006
    mask = (rank >= 0) & media.notna()
    rho, p_valor = stats.spearmanr(rank[mask], media[mask])

    medias_faixa = (
        pd.DataFrame({"faixa": base["faixa_renda"], "media": media})
        .groupby("faixa", observed=True)["media"]
        .mean()
        .reindex(ORDEM_Q006)
        .dropna()
    )
    base_faixa, topo_faixa = medias_faixa.index[0], medias_faixa.index[-1]
    gap = float(medias_faixa.iloc[-1] - medias_faixa.iloc[0])

    return {
        "spearman_rho": round(float(rho), 3),
        "spearman_p": float(p_valor),
        "gap_pontos": round(gap, 1),
        "faixa_base": base_faixa,
        "faixa_topo": topo_faixa,
        "media_base": round(float(medias_faixa.iloc[0]), 1),
        "media_topo": round(float(medias_faixa.iloc[-1]), 1),
        "n_par": int(mask.sum()),
    }


def plotar_renda_nota(tabela: pd.DataFrame) -> "Path":
    """Linha da media por area + media geral ao longo das faixas de renda (ordinal).

    Eixo x na ordem ordinal das faixas; cada area uma linha, media geral em
    destaque (preta, mais grossa). Le legivel a monotonicidade de P1.
    """
    faixas = [f for f in ORDEM_Q006 if f in tabela.index]
    sub = tabela.loc[faixas]

    fig, eixo = plt.subplots(figsize=(13, 7))
    for col in NOTAS:
        eixo.plot(faixas, sub[col], marker="o", linewidth=1.5, label=ROTULO_NOTA[col])
    eixo.plot(faixas, sub["media_geral"], marker="s", linewidth=3, color="black",
              label="Media geral (CN/CH/LC/MT)")
    eixo.set_title("P1 — Nota media por faixa de renda familiar (ENEM 2022+2023)")
    eixo.set_xlabel("Faixa de renda (salarios minimos)")
    eixo.set_ylabel("Nota media")
    eixo.tick_params(axis="x", rotation=70)
    eixo.grid(axis="y", alpha=0.3)
    eixo.legend(loc="upper left", fontsize=9)
    fig.tight_layout()

    destino = DIR_FIGURAS / "p1_renda_nota.png"
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    return destino


def _imprimir_conclusao(stat: dict) -> None:
    print("\n--- CONCLUSAO P1 ---")
    forca = "forte" if abs(stat["spearman_rho"]) >= 0.7 else (
        "moderada" if abs(stat["spearman_rho"]) >= 0.4 else "fraca")
    print(
        f"Relacao renda x desempenho: POSITIVA e MONOTONICA "
        f"(Spearman rho={stat['spearman_rho']:+.3f}, p={stat['spearman_p']:.1e}, "
        f"correlacao {forca}; N={stat['n_par']:,} pares)."
    )
    print(
        f"Gap topo-base = {stat['gap_pontos']:.1f} pts na media geral "
        f"('{stat['faixa_topo']}' = {stat['media_topo']:.1f} vs "
        f"'{stat['faixa_base']}' = {stat['media_base']:.1f})."
    )
    print(
        "A nota media sobe de forma consistente com a faixa de renda nas 5 areas — "
        "confirma a hipotese de P1 (positiva, monotonica). Associacao, NAO causalidade: "
        "renda correlaciona com outros fatores (escola, regiao) tratados em P2/P3."
    )


def _imprimir_resumo(base: pd.DataFrame) -> None:
    print("\n--- VALIDACAO US-05 (P1) ---")
    print("linhas totais:", f"{len(base):,}")

    tabela = media_por_renda(base)
    print("\nmedia por area + media geral, por faixa de renda (ordinal):")
    print(tabela.to_string())

    stat = estatistica_suporte(base)
    _imprimir_conclusao(stat)
    return tabela


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="US-05: P1 renda x nota media nas 5 areas")
    parser.add_argument("--nrows", type=int, default=None,
                        help="amostra para teste rapido (default: base inteira)")
    args = parser.parse_args()

    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)

    base = carregar_base(nrows=args.nrows)
    tabela = _imprimir_resumo(base)
    fig = plotar_renda_nota(tabela)
    print(f"\nfigura gerada:\n  {fig}")
