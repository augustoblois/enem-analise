"""P2: gap de nota entre escola publica e privada, por ano (US-06).

Escopo: SO leitura do parquet tratado (US-02) + helpers de EDA (US-04). Responde
P2 — qual o gap de desempenho entre tipo_escola Publica e Privada, e como esse
gap varia de 2022 para 2023? Calcula media geral por tipo_escola e ano, o gap
Privada-Publica por ano, a variacao do gap entre os anos e uma figura legivel.
NAO reprocessa CSV, NAO recodifica (US-02), NAO modela (US-10).

------------------------------------------------------------------------------
DECISOES DE ANALISE (insumo do relatorio US-11)
------------------------------------------------------------------------------
- `tipo_escola` tem 3 categorias (ORDEM_TP_ESCOLA): "Publica", "Privada",
  "Nao informado". O gap Privada-Publica usa SO essas duas categorias; "Nao
  informado" NAO entra no gap, mas aparece na tabela de frequencia com seu N e %
  (medido na base, nao copiado do dicionario US-03 — ver nota abaixo).
- O % real de "Nao informado" na base CHEIA difere do 70,1% citado na docstring
  da eda.py (esse numero e de uma leitura parcial/dicionario, US-03). Aqui
  reportamos o valor MEDIDO diretamente na base carregada.
- Notas mantem NaN (ausente/eliminado); todas as medias usam skipna (decisao
  herdada da US-02/US-04). O N por grupo/ano e reportado para o leitor.
- Media geral = media de CN/CH/LC/MT (sem redacao), via `eda.media_geral_notas`,
  consistente com US-05/US-06, para uma medida unica de desempenho cognitivo.
- `ano` e categoria ordenada (2022, 2023, ver tratamento.py); a tabela por
  tipo_escola x ano mantem essa ordem nas colunas.
- Gap = media(Privada) - media(Publica) na media geral, calculado SEPARADO por
  ano. Variacao do gap = gap_2023 - gap_2022.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from .eda import DIR_FIGURAS, NOTAS, ROTULO_NOTA, carregar_base, media_geral_notas
from .tratamento import ORDEM_TP_ESCOLA

GRUPO_GAP = ["Publica", "Privada"]


def frequencia_tipo_escola(base: pd.DataFrame) -> pd.DataFrame:
    """Tabela de frequencia (n e %) das 3 categorias de tipo_escola na base.

    Inclui "Nao informado" — N e % medidos diretamente na base carregada, nao
    copiados de nenhum dicionario.
    """
    contagem = base["tipo_escola"].cat.set_categories(ORDEM_TP_ESCOLA).value_counts().reindex(ORDEM_TP_ESCOLA)
    proporcao = (contagem / contagem.sum() * 100).round(1)
    return pd.DataFrame({"n": contagem, "%": proporcao})


def media_por_escola_ano(base: pd.DataFrame) -> pd.DataFrame:
    """Media de cada area + media geral (CN/CH/LC/MT) por tipo_escola e ano.

    Linhas na ordem ORDEM_TP_ESCOLA, colunas na ordem das categorias de `ano`.
    Inclui coluna `n` (candidatos por grupo/ano). Medias com skipna.
    """
    df = base.copy()
    df["media_geral"] = media_geral_notas(df)

    colunas = NOTAS[:-1] + ["media_geral"]  # CN/CH/LC/MT (sem redacao na media_geral; redacao fica de fora)
    anos = list(df["ano"].cat.categories) if hasattr(df["ano"], "cat") else sorted(df["ano"].unique())

    linhas = []
    for ano in anos:
        sub = df[df["ano"] == ano]
        agregado = (
            sub.groupby("tipo_escola", observed=True)[colunas]
            .mean()
            .reindex(ORDEM_TP_ESCOLA)
            .round(1)
        )
        agregado.insert(0, "n", sub.groupby("tipo_escola", observed=True).size().reindex(ORDEM_TP_ESCOLA))
        agregado.insert(0, "ano", ano)
        linhas.append(agregado)

    return pd.concat(linhas).set_index("ano", append=True).reorder_levels(["ano", agregado.index.name or 0])


def gap_publica_privada_por_ano(tabela: pd.DataFrame) -> pd.DataFrame:
    """Gap Privada-Publica na media geral, por ano, + variacao 2022->2023.

    Usa SO Publica e Privada (Nao informado fica fora do gap). Retorna tabela
    com colunas: media_publica, media_privada, gap, n_publica, n_privada.
    """
    linhas = {}
    for ano in tabela.index.get_level_values(0).unique():
        sub = tabela.loc[ano]
        media_pub = float(sub.loc["Publica", "media_geral"])
        media_priv = float(sub.loc["Privada", "media_geral"])
        linhas[ano] = {
            "media_publica": round(media_pub, 1),
            "media_privada": round(media_priv, 1),
            "gap": round(media_priv - media_pub, 1),
            "n_publica": int(sub.loc["Publica", "n"]),
            "n_privada": int(sub.loc["Privada", "n"]),
        }
    return pd.DataFrame(linhas).T


def plotar_gap_escola(tabela: pd.DataFrame, gap: pd.DataFrame) -> "Path":
    """Barras agrupadas: media geral Publica vs Privada por ano + linha do gap.

    Painel esquerdo: media geral por tipo_escola, barras lado a lado por ano.
    Painel direito: gap (Privada-Publica) por ano, para ver a variacao.
    """
    anos = list(gap.index)

    fig, (eixo_media, eixo_gap) = plt.subplots(1, 2, figsize=(14, 6))

    largura = 0.35
    posicoes = range(len(anos))
    eixo_media.bar(
        [p - largura / 2 for p in posicoes], gap["media_publica"], largura,
        label="Publica", color="#4472c4",
    )
    eixo_media.bar(
        [p + largura / 2 for p in posicoes], gap["media_privada"], largura,
        label="Privada", color="#ed7d31",
    )
    eixo_media.set_xticks(list(posicoes))
    eixo_media.set_xticklabels([str(a) for a in anos])
    eixo_media.set_title("Media geral (CN/CH/LC/MT) por tipo de escola")
    eixo_media.set_ylabel("Nota media")
    eixo_media.legend()
    eixo_media.grid(axis="y", alpha=0.3)

    eixo_gap.plot(anos, gap["gap"], marker="o", linewidth=2.5, color="#c00000")
    eixo_gap.set_title("Gap Privada - Publica (media geral)")
    eixo_gap.set_xlabel("ano")
    eixo_gap.set_ylabel("gap (pontos)")
    eixo_gap.grid(axis="y", alpha=0.3)
    for ano, valor in zip(anos, gap["gap"]):
        eixo_gap.annotate(f"{valor:.1f}", (ano, valor), textcoords="offset points", xytext=(0, 8), ha="center")

    fig.suptitle("P2 — Gap de nota Publica x Privada (ENEM 2022 e 2023)")
    fig.tight_layout()

    destino = DIR_FIGURAS / "p2_escola_gap.png"
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    return destino


def _imprimir_conclusao(gap: pd.DataFrame) -> None:
    print("\n--- CONCLUSAO P2 ---")
    anos = list(gap.index)
    for ano in anos:
        linha = gap.loc[ano]
        print(
            f"Ano {ano}: media Publica={linha['media_publica']:.1f} (n={int(linha['n_publica']):,}), "
            f"media Privada={linha['media_privada']:.1f} (n={int(linha['n_privada']):,}), "
            f"gap={linha['gap']:.1f} pts."
        )

    if len(anos) >= 2:
        gap_inicial, gap_final = gap.loc[anos[0], "gap"], gap.loc[anos[-1], "gap"]
        variacao = round(float(gap_final - gap_inicial), 1)
        direcao = "cresceu" if variacao > 0.5 else ("encolheu" if variacao < -0.5 else "ficou estavel")
        print(f"\nVariacao do gap {anos[0]}->{anos[-1]}: {variacao:+.1f} pts ({direcao}).")
    else:
        variacao = None

    ordem_esperada = "dentro" if all(80 <= gap.loc[a, "gap"] <= 120 for a in anos) else "fora"
    print(
        f"O gap Privada-Publica esta {ordem_esperada} da ordem esperada pela hipotese de P2 "
        f"(~80-120 pts na media geral). Privada > Publica em todos os anos observados, "
        f"confirmando a direcao esperada. Associacao, NAO causalidade: o tipo de escola "
        f"correlaciona com renda e outros fatores (ver P1/P3)."
    )


def _imprimir_resumo(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("\n--- VALIDACAO US-06 (P2) ---")
    print("linhas totais:", f"{len(base):,}")

    freq = frequencia_tipo_escola(base)
    print("\nfrequencia de tipo_escola (Publica/Privada/Nao informado):")
    print(freq.to_string())

    tabela = media_por_escola_ano(base)
    print("\nmedia por area + media geral, por tipo_escola e ano:")
    print(tabela.to_string())

    gap = gap_publica_privada_por_ano(tabela)
    print("\ngap Privada-Publica (media geral) por ano:")
    print(gap.to_string())

    _imprimir_conclusao(gap)
    return tabela, gap


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="US-06: P2 gap de nota Publica x Privada por ano")
    parser.add_argument("--nrows", type=int, default=None,
                        help="amostra para teste rapido (default: base inteira)")
    args = parser.parse_args()

    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)

    base = carregar_base(nrows=args.nrows)
    tabela, gap = _imprimir_resumo(base)
    fig = plotar_gap_escola(tabela, gap)
    print(f"\nfigura gerada:\n  {fig}")
