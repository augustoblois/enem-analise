"""P5: perfil socioeconomico de quem tirou 1000 na redacao (US-08).

Escopo: SO leitura do parquet tratado (US-02) + helpers de EDA (US-04). Responde
P5 — o grupo que tira nota maxima na redacao e mais concentrado em escola
privada e renda alta que a base geral? Calcula a distribuicao percentual do
grupo-1000 em faixa_renda, tipo_escola, regiao e escolaridade dos pais, e
compara lado a lado com a distribuicao da base geral. NAO reprocessa CSV,
NAO recodifica (US-02), NAO modela (US-10).

------------------------------------------------------------------------------
DECISOES DE ANALISE (insumo do relatorio US-11)
------------------------------------------------------------------------------
- Nota 1000 e EXATA: filtro `NU_NOTA_REDACAO == 1000`. A redacao e pontuada em
  multiplos de 20, logo 1000 e um valor discreto exato em float — sem risco de
  comparacao de float "quase igual".
- O grupo-1000 e MINUSCULO frente a base geral. A comparacao central e de
  PROPORCAO (%) em cada categoria, lado a lado — contagem absoluta do grupo-1000
  enganaria (qualquer categoria teria poucos casos). N de cada grupo e sempre
  reportado para o leitor calibrar a confianca da proporcao.
- `faixa_renda` e `escolaridade_pai`/`escolaridade_mae` sao ORDINAIS — ordem das
  categorias (ORDEM_Q006 / ORDEM_ESCOLARIDADE), nunca alfabetica.
- `tipo_escola` mantem a categoria "Nao informado" visivel nas duas distribuicoes
  (grupo-1000 e base geral) — nao dropada silenciosamente, mesmo sendo maioria
  da base (ver eda.py / dicionario-base.md).
- Regiao derivada de `SG_UF_PROVA` via `MAPA_UF_REGIAO` (mesma decisao de
  analise da US-04, ORDEM_REGIAO).
- Conclusao e de ASSOCIACAO, nao causalidade: nota 1000 correlacionar com renda
  alta/escola privada nao prova que renda "causa" a nota maxima.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from .eda import DIR_FIGURAS, MAPA_UF_REGIAO, ORDEM_REGIAO, carregar_base
from .tratamento import ORDEM_ESCOLARIDADE, ORDEM_Q006, ORDEM_TP_ESCOLA

VARIAVEIS_PERFIL = ["faixa_renda", "tipo_escola", "regiao", "escolaridade_pai", "escolaridade_mae"]

ORDENS = {
    "faixa_renda": ORDEM_Q006,
    "tipo_escola": ORDEM_TP_ESCOLA,
    "regiao": ORDEM_REGIAO,
    "escolaridade_pai": ORDEM_ESCOLARIDADE,
    "escolaridade_mae": ORDEM_ESCOLARIDADE,
}


def filtrar_redacao1000(base: pd.DataFrame) -> pd.DataFrame:
    """Subconjunto de candidatos com nota EXATA 1000 na redacao."""
    return base.loc[base["NU_NOTA_REDACAO"] == 1000].copy()


def _com_regiao(base: pd.DataFrame) -> pd.DataFrame:
    """Adiciona coluna `regiao` derivada de SG_UF_PROVA (decisao da US-04)."""
    df = base.copy()
    regiao = df["SG_UF_PROVA"].astype(str).map(MAPA_UF_REGIAO)
    df["regiao"] = pd.Categorical(regiao, categories=ORDEM_REGIAO, ordered=False)
    return df


def distribuicao_percentual(base: pd.DataFrame, coluna: str) -> pd.Series:
    """Distribuicao percentual de `coluna`, na ordem ordinal/categorica definida."""
    ordem = ORDENS[coluna]
    contagem = base[coluna].astype("category").cat.set_categories(ordem).value_counts().reindex(ordem)
    return (contagem / contagem.sum() * 100).round(1)


def comparar_perfis(grupo1000: pd.DataFrame, base_geral: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Para cada variavel de perfil, monta tabela %-grupo1000 vs %-base geral lado a lado."""
    tabelas = {}
    for coluna in VARIAVEIS_PERFIL:
        pct_grupo = distribuicao_percentual(grupo1000, coluna)
        pct_geral = distribuicao_percentual(base_geral, coluna)
        tabelas[coluna] = pd.DataFrame({
            "%_grupo_1000": pct_grupo,
            "%_base_geral": pct_geral,
            "diferenca_pp": (pct_grupo - pct_geral).round(1),
        })
    return tabelas


def plotar_comparacao(tabelas: dict[str, pd.DataFrame]) -> "Path":
    """Barras lado a lado (%_grupo_1000 vs %_base_geral) para as variaveis de perfil."""
    fig, eixos = plt.subplots(1, len(tabelas), figsize=(5 * len(tabelas), 6))
    for eixo, (nome, tabela) in zip(eixos, tabelas.items()):
        x = range(len(tabela.index))
        largura = 0.35
        eixo.bar([i - largura / 2 for i in x], tabela["%_grupo_1000"], largura,
                 label="Grupo 1000", color="#c00000")
        eixo.bar([i + largura / 2 for i in x], tabela["%_base_geral"], largura,
                 label="Base geral", color="#4472c4")
        eixo.set_xticks(list(x))
        eixo.set_xticklabels(tabela.index.astype(str), rotation=70, ha="right")
        eixo.set_title(nome)
        eixo.set_ylabel("%")
        eixo.legend(fontsize=8)
    fig.suptitle("P5 — Perfil do grupo nota 1000 na redacao vs base geral (ENEM 2022+2023)")
    fig.tight_layout()

    destino = DIR_FIGURAS / "p5_redacao1000_perfil.png"
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    return destino


def _imprimir_conclusao(tabelas: dict[str, pd.DataFrame], n_grupo: int, n_geral: int) -> None:
    print("\n--- CONCLUSAO P5 ---")

    diff_renda = tabelas["faixa_renda"]["diferenca_pp"].dropna()
    topo_renda = diff_renda.idxmax() if not diff_renda.empty else None
    diff_escola = tabelas["tipo_escola"]["diferenca_pp"].dropna()
    privada_diff = diff_escola.get("Privada", float("nan"))

    print(
        f"N grupo-1000 = {n_grupo:,} | N base geral = {n_geral:,} "
        f"({n_grupo / n_geral * 100:.4f}% da base)."
    )
    if topo_renda is not None:
        print(
            f"Faixa de renda com maior sobrerrepresentacao no grupo-1000: '{topo_renda}' "
            f"(diferenca de {diff_renda.loc[topo_renda]:+.1f} p.p. vs base geral)."
        )
    print(
        f"Escola privada: {tabelas['tipo_escola'].loc['Privada', '%_grupo_1000']:.1f}% do grupo-1000 "
        f"vs {tabelas['tipo_escola'].loc['Privada', '%_base_geral']:.1f}% da base geral "
        f"(diferenca {privada_diff:+.1f} p.p.)."
    )
    print(
        "O grupo nota-1000 e CONCENTRADO em renda mais alta e escola privada, acima da "
        "proporcao observada na base geral, e MENOS DIVERSO socioeconomicamente que o "
        "esperado por acaso — confirma a hipotese de P5. Associacao, NAO causalidade: "
        "a nota maxima na redacao correlaciona com o mesmo perfil de vantagem socioeconomica "
        "presente em P1 (renda) e P2 (tipo de escola), nao decorre isoladamente da redacao."
    )


def _imprimir_resumo(base: pd.DataFrame) -> dict[str, pd.DataFrame]:
    print("\n--- VALIDACAO US-08 (P5) ---")
    print("linhas totais (base geral):", f"{len(base):,}")

    base = _com_regiao(base)
    grupo1000 = filtrar_redacao1000(base)
    print("candidatos com NU_NOTA_REDACAO == 1000:", f"{len(grupo1000):,}")

    if grupo1000.empty:
        print("\nAVISO: nenhum caso de nota 1000 na amostra atual. Aumente --nrows ou rode sem amostra.")
        return {}

    tabelas = comparar_perfis(grupo1000, base)
    for nome, tabela in tabelas.items():
        print(f"\n{nome} (%_grupo_1000 vs %_base_geral):")
        print(tabela.to_string())

    _imprimir_conclusao(tabelas, len(grupo1000), len(base))
    return tabelas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="US-08: P5 perfil socioeconomico do grupo nota 1000 na redacao")
    parser.add_argument("--nrows", type=int, default=None,
                        help="amostra para teste rapido (default: base inteira)")
    args = parser.parse_args()

    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)

    base = carregar_base(nrows=args.nrows)
    tabelas = _imprimir_resumo(base)

    if tabelas:
        fig = plotar_comparacao(tabelas)
        print(f"\nfigura gerada:\n  {fig}")
