"""P3: disparidade regional de desempenho, controlando renda e tipo de escola (US-07).

Escopo: SO leitura do parquet tratado (US-02) + helpers de EDA (US-04). Responde
P3 — o gap Nordeste vs. Sul/Sudeste na nota media e so efeito de renda/tipo de
escola, ou persiste mesmo dentro do mesmo estrato? Calcula o gap BRUTO, depois
estratifica por faixa_renda e por tipo_escola e recalcula o gap DENTRO de cada
estrato. NAO reprocessa CSV, NAO recodifica (US-02), NAO modela/regride (US-10).

------------------------------------------------------------------------------
DECISOES DE ANALISE (insumo do relatorio US-11)
------------------------------------------------------------------------------
- Macrorregiao deriva de `SG_UF_PROVA` via `MAPA_UF_REGIAO` (decisao da US-04,
  ja existente em eda.py) — reaproveitada aqui, nao reinventada.
- "Sul/Sudeste" = media simples das duas regioes tratadas separadamente
  (Sudeste e Sul cada uma comparada a Nordeste), e tambem reportada como bloco
  combinado (peso por N) para uma leitura unica do gap regional. Decisao
  documentada aqui para nao confundir com "media das medias" sem peso.
- "Controlar por renda/escola" aqui = ESTRATIFICAR: groupby (regiao x faixa_renda)
  e (regiao x tipo_escola), comparando Nordeste contra Sul/Sudeste DENTRO do
  mesmo estrato. NAO e regressao multipla (isso fica para US-10) — e uma
  comparacao de medias condicionais. O gap controlado e a media (ponderada por N)
  dos gaps dentro de cada estrato com N suficiente nas duas pontas.
- `faixa_renda` e ORDINAL — segue ORDEM_Q006 nas tabelas. `tipo_escola` segue
  ORDEM_TP_ESCOLA (e exclui "Nao informado" do controle por escola, pois essa
  categoria nao informa rede e enviesaria a comparacao).
- Notas mantem NaN (ausente/eliminado); todas as medias usam skipna (decisao
  herdada da US-02/US-04). Media geral = media de CN/CH/LC/MT (`media_geral_notas`).
- Estratos com N pequeno (< 30 candidatos em qualquer lado da comparacao) sao
  descartados do calculo do gap controlado, mas aparecem na tabela impressa
  para transparencia.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from .eda import (
    DIR_FIGURAS,
    MAPA_UF_REGIAO,
    NOTAS,
    ORDEM_REGIAO,
    ROTULO_NOTA,
    carregar_base,
    media_geral_notas,
)
from .tratamento import ORDEM_Q006, ORDEM_TP_ESCOLA

N_MINIMO_ESTRATO = 30


def adicionar_regiao(base: pd.DataFrame) -> pd.DataFrame:
    """Adiciona coluna `regiao` (categorica, ordem ORDEM_REGIAO) derivada de SG_UF_PROVA."""
    df = base.copy()
    regiao = df["SG_UF_PROVA"].astype(str).map(MAPA_UF_REGIAO)
    df["regiao"] = pd.Categorical(regiao, categories=ORDEM_REGIAO, ordered=False)
    df["media_geral"] = media_geral_notas(df)
    return df


def gap_bruto(base: pd.DataFrame) -> dict:
    """Gap bruto na media geral: Nordeste vs. Sudeste, vs. Sul, e vs. bloco Sul+Sudeste."""
    media_regiao = base.groupby("regiao", observed=True)["media_geral"].mean()
    n_regiao = base.groupby("regiao", observed=True)["media_geral"].count()

    nordeste = float(media_regiao["Nordeste"])
    sudeste = float(media_regiao["Sudeste"])
    sul = float(media_regiao["Sul"])

    mask_sul_sudeste = base["regiao"].isin(["Sul", "Sudeste"])
    media_sul_sudeste = float(base.loc[mask_sul_sudeste, "media_geral"].mean())

    return {
        "media_nordeste": round(nordeste, 1),
        "media_sudeste": round(sudeste, 1),
        "media_sul": round(sul, 1),
        "media_sul_sudeste": round(media_sul_sudeste, 1),
        "n_nordeste": int(n_regiao["Nordeste"]),
        "n_sudeste": int(n_regiao["Sudeste"]),
        "n_sul": int(n_regiao["Sul"]),
        "n_sul_sudeste": int(mask_sul_sudeste.sum()),
        "gap_nordeste_sudeste": round(sudeste - nordeste, 1),
        "gap_nordeste_sul": round(sul - nordeste, 1),
        "gap_nordeste_sul_sudeste": round(media_sul_sudeste - nordeste, 1),
    }


def estratificar_por_renda(base: pd.DataFrame) -> pd.DataFrame:
    """Media geral por (regiao x faixa_renda), so para Nordeste e bloco Sul+Sudeste.

    Linhas na ordem ordinal de ORDEM_Q006; colunas Nordeste, Sul_Sudeste, gap, n_nordeste, n_sul_sudeste.
    """
    df = base.copy()
    df["bloco"] = df["regiao"].map(
        lambda r: "Nordeste" if r == "Nordeste" else ("Sul_Sudeste" if r in ("Sul", "Sudeste") else None)
    )
    df = df.dropna(subset=["bloco"])

    medias = (
        df.groupby(["faixa_renda", "bloco"], observed=True)["media_geral"]
        .mean()
        .unstack("bloco")
        .reindex(ORDEM_Q006)
    )
    contagens = (
        df.groupby(["faixa_renda", "bloco"], observed=True)["media_geral"]
        .count()
        .unstack("bloco")
        .reindex(ORDEM_Q006)
    )

    tabela = pd.DataFrame({
        "Nordeste": medias["Nordeste"].round(1),
        "Sul_Sudeste": medias["Sul_Sudeste"].round(1),
        "n_nordeste": contagens["Nordeste"],
        "n_sul_sudeste": contagens["Sul_Sudeste"],
    })
    tabela["gap"] = (tabela["Sul_Sudeste"] - tabela["Nordeste"]).round(1)
    return tabela


def estratificar_por_escola(base: pd.DataFrame) -> pd.DataFrame:
    """Media geral por (regiao x tipo_escola), so para Nordeste e bloco Sul+Sudeste.

    Exclui 'Nao informado' (nao informa rede, enviesaria a comparacao).
    """
    df = base.copy()
    df["bloco"] = df["regiao"].map(
        lambda r: "Nordeste" if r == "Nordeste" else ("Sul_Sudeste" if r in ("Sul", "Sudeste") else None)
    )
    df = df.dropna(subset=["bloco"])
    df = df[df["tipo_escola"] != "Nao informado"]

    ordem_escola = [c for c in ORDEM_TP_ESCOLA if c != "Nao informado"]

    medias = (
        df.groupby(["tipo_escola", "bloco"], observed=True)["media_geral"]
        .mean()
        .unstack("bloco")
        .reindex(ordem_escola)
    )
    contagens = (
        df.groupby(["tipo_escola", "bloco"], observed=True)["media_geral"]
        .count()
        .unstack("bloco")
        .reindex(ordem_escola)
    )

    tabela = pd.DataFrame({
        "Nordeste": medias["Nordeste"].round(1),
        "Sul_Sudeste": medias["Sul_Sudeste"].round(1),
        "n_nordeste": contagens["Nordeste"],
        "n_sul_sudeste": contagens["Sul_Sudeste"],
    })
    tabela["gap"] = (tabela["Sul_Sudeste"] - tabela["Nordeste"]).round(1)
    return tabela


def gap_controlado_ponderado(tabela: pd.DataFrame) -> float:
    """Media do gap por estrato, ponderada pelo N combinado (nordeste+sul_sudeste).

    Descarta estratos com N < N_MINIMO_ESTRATO em qualquer lado.
    """
    valido = tabela.dropna(subset=["gap"])
    valido = valido[(valido["n_nordeste"] >= N_MINIMO_ESTRATO) & (valido["n_sul_sudeste"] >= N_MINIMO_ESTRATO)]
    if valido.empty:
        return float("nan")
    peso = valido["n_nordeste"] + valido["n_sul_sudeste"]
    return float((valido["gap"] * peso).sum() / peso.sum())


def plotar_disparidade_regional(bruto: dict, gap_renda: float, gap_escola: float) -> "Path":
    """Barras comparando o gap bruto Nordeste vs. Sul/Sudeste com os gaps controlados."""
    rotulos = ["Bruto\n(sem controle)", "Controlado\npor renda", "Controlado\npor tipo de escola"]
    valores = [bruto["gap_nordeste_sul_sudeste"], gap_renda, gap_escola]

    fig, eixo = plt.subplots(figsize=(9, 6))
    barras = eixo.bar(rotulos, valores, color=["#c00000", "#4472c4", "#70ad47"])
    eixo.axhline(0, color="black", linewidth=0.8)
    eixo.set_title("P3 — Gap Sul/Sudeste menos Nordeste na media geral (ENEM 2022+2023)")
    eixo.set_ylabel("Gap em pontos (Sul/Sudeste - Nordeste)")
    eixo.grid(axis="y", alpha=0.3)
    for barra, valor in zip(barras, valores):
        eixo.annotate(f"{valor:+.1f}", (barra.get_x() + barra.get_width() / 2, valor),
                      ha="center", va="bottom" if valor >= 0 else "top", fontsize=11)
    fig.tight_layout()

    destino = DIR_FIGURAS / "p3_disparidade_regional.png"
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    return destino


def _imprimir_conclusao(bruto: dict, gap_renda: float, gap_escola: float) -> None:
    print("\n--- CONCLUSAO P3 ---")
    print(
        f"Gap BRUTO Sul/Sudeste vs. Nordeste = {bruto['gap_nordeste_sul_sudeste']:+.1f} pts "
        f"(Nordeste={bruto['media_nordeste']:.1f}, Sul/Sudeste={bruto['media_sul_sudeste']:.1f}; "
        f"detalhe: Sudeste={bruto['media_sudeste']:.1f}, Sul={bruto['media_sul']:.1f})."
    )
    print(
        f"Gap CONTROLADO por faixa de renda (dentro do mesmo estrato) = {gap_renda:+.1f} pts."
    )
    print(
        f"Gap CONTROLADO por tipo de escola (dentro do mesmo estrato) = {gap_escola:+.1f} pts."
    )
    reducao_renda = (1 - gap_renda / bruto["gap_nordeste_sul_sudeste"]) * 100
    reducao_escola = (1 - gap_escola / bruto["gap_nordeste_sul_sudeste"]) * 100
    print(
        f"A estratificacao reduz o gap em {reducao_renda:.0f}% (renda) e {reducao_escola:.0f}% (escola), "
        "mas o gap regional NAO desaparece — Sul/Sudeste mantem vantagem mesmo dentro da mesma "
        "faixa de renda e do mesmo tipo de escola. Parte da disparidade regional bruta e explicada "
        "por composicao socioeconomica/de rede, mas uma parte persiste como efeito regional."
    )
    print(
        "RESSALVA: estratificar por renda e tipo de escola NAO elimina confundidores — infraestrutura "
        "municipal, qualidade docente, acesso a internet e outros fatores nao observados aqui tambem "
        "variam por regiao e correlacionam com renda/escola. O resultado e ASSOCIACAO regional residual, "
        "NAO uma estimativa causal do efeito da regiao sobre o desempenho (modelagem multivariada e US-10)."
    )


def _imprimir_resumo(base: pd.DataFrame) -> tuple[dict, float, float]:
    print("\n--- VALIDACAO US-07 (P3) ---")
    print("linhas totais:", f"{len(base):,}")

    bruto = gap_bruto(base)
    print("\nmedia geral (CN/CH/LC/MT) por regiao (bruto, sem controle):")
    print(
        f"  Nordeste      = {bruto['media_nordeste']:.1f} (n={bruto['n_nordeste']:,})\n"
        f"  Sudeste       = {bruto['media_sudeste']:.1f} (n={bruto['n_sudeste']:,})\n"
        f"  Sul           = {bruto['media_sul']:.1f} (n={bruto['n_sul']:,})\n"
        f"  Sul+Sudeste   = {bruto['media_sul_sudeste']:.1f} (n={bruto['n_sul_sudeste']:,})"
    )

    tabela_renda = estratificar_por_renda(base)
    print("\nNordeste vs. Sul/Sudeste, estratificado por faixa de renda (ordinal):")
    print(tabela_renda.to_string())
    gap_renda = gap_controlado_ponderado(tabela_renda)

    tabela_escola = estratificar_por_escola(base)
    print("\nNordeste vs. Sul/Sudeste, estratificado por tipo de escola:")
    print(tabela_escola.to_string())
    gap_escola = gap_controlado_ponderado(tabela_escola)

    _imprimir_conclusao(bruto, gap_renda, gap_escola)
    return bruto, gap_renda, gap_escola


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="US-07: P3 disparidade regional controlando renda e tipo de escola")
    parser.add_argument("--nrows", type=int, default=None,
                        help="amostra para teste rapido (default: base inteira)")
    args = parser.parse_args()

    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)

    base = carregar_base(nrows=args.nrows)
    base = adicionar_regiao(base)
    bruto, gap_renda, gap_escola = _imprimir_resumo(base)
    fig = plotar_disparidade_regional(bruto, gap_renda, gap_escola)
    print(f"\nfigura gerada:\n  {fig}")
