"""Modulo vivo: recalculo de P2/P3 sobre a edicao ingerida (US-21, EP-07).

Escopo (SO US-21): calcular P2 (gap Publica x Privada) e P3 (disparidade
Nordeste x Sul/Sudeste) sobre o DataFrame NORMALIZADO produzido pelo modulo
vivo (`modulo_vivo.carregar_edicao_viva`), por `ano`, e CONSOLIDAR essas
metricas numa saida comparavel entre edicoes (2022/2023/2024). NAO ingere
dados (isso e US-20) e NAO atualiza dashboard/relatorio (isso e US-22/US-23).

ISOLAMENTO DO NUCLEO SES (RNF-07): este arquivo importa SO de `modulo_vivo`
(constantes/carregador da propria US-20). NAO importa `carga.py`,
`tratamento.py`, `eda.py` nem qualquer funcao que leia a base SES tratada
(parquet de 2022+2023). Em particular, a media geral NAO usa
`eda.media_geral_notas` (que pressupoe o pipeline/parquet SES) — a definicao
de media geral (CN/CH/LC/MT, skipna, sem redacao) e REPLICADA localmente em
`_media_geral` a partir das colunas normalizadas do proprio modulo vivo
(`nota_cn/nota_ch/nota_lc/nota_mt`), evitando qualquer dependencia do core.

------------------------------------------------------------------------------
DEFINICOES REPLICADAS (mesma logica de p2_escola.py / p3_regiao.py)
------------------------------------------------------------------------------
- Media geral = media(nota_cn, nota_ch, nota_lc, nota_mt), skipna, SEM redacao
  (mesma decisao de US-05/US-06/US-07, agora sobre as colunas normalizadas
  nota_cn/ch/lc/mt do schema-alvo da US-20, em vez de NU_NOTA_*).
- P2 (gap escola): gap = media(Privada) - media(Publica) na media geral, por
  ano. "Nao informado" fica fora do gap, mas aparece na tabela de frequencia
  (visivel, nao descartado silenciosamente).
- P3 (disparidade regional): media geral por regiao, por ano; gap = media do
  bloco Sul+Sudeste (media simples ponderada por N, igual a p3_regiao.py)
  menos a media do Nordeste.

------------------------------------------------------------------------------
PERSISTENCIA PARA O DASHBOARD (US-22, ponto de insercao da edicao viva)
------------------------------------------------------------------------------
A saida consolidada (ano, metrica, valor) e gravada em
`CAMINHO_PARQUET_VIVO` (data/processado/modulo_vivo_p2_p3.parquet, fora do
git, RNF-04). O dashboard (`dashboard.py`) SO LE esse parquet via
`carregar_metricas_vivas` — nunca recalcula on-demand nem importa
`modulo_vivo`/`carregar_edicao_viva` diretamente, preservando o isolamento do
nucleo SES (RNF-07) tambem no lado do consumo.

Para incorporar uma edicao nova (ex. 2025) ao dashboard, basta rodar:

    python -m src.enem.modulo_vivo_metricas --atualizar

Isso varre TODOS os anos mapeados em `modulo_vivo.LAYOUTS` cujo CSV de
RESULTADOS exista no disco, recalcula P2/P3 de cada um e regrava o parquet
consolidado por completo (sem editar codigo, sem passo manual extra). Anos
mapeados sem CSV no disco sao pulados (logado, nao e erro).
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass

import pandas as pd

from .modulo_vivo import LAYOUTS, NOTAS_ALVO, ORDEM_TP_ESCOLA, RAIZ_PROJETO, carregar_edicao_viva

logger = logging.getLogger(__name__)

COLUNAS_MEDIA_GERAL = ["nota_cn", "nota_ch", "nota_lc", "nota_mt"]

# Destino do parquet consolidado de P2/P3 vivo (US-22, fora do git, RNF-04).
# Separado de `tratamento.CAMINHO_PARQUET` (nucleo SES) — ver docstring do modulo.
CAMINHO_PARQUET_VIVO = RAIZ_PROJETO / "data" / "processado" / "modulo_vivo_p2_p3.parquet"


def _media_geral(base: pd.DataFrame) -> pd.Series:
    """Media geral (CN/CH/LC/MT, skipna, sem redacao) sobre o schema-alvo do
    modulo vivo. Replica a definicao de `eda.media_geral_notas` SEM importar
    de `eda.py`, preservando o isolamento do nucleo SES (RNF-07).
    """
    return base[COLUNAS_MEDIA_GERAL].mean(axis=1, skipna=True)


@dataclass(frozen=True, slots=True)
class ResultadoP2:
    """Saida de P2 para um `ano`: media/gap Publica x Privada + frequencia."""

    ano: int
    media_publica: float
    media_privada: float
    gap: float
    n_publica: int
    n_privada: int
    n_nao_informado: int


@dataclass(frozen=True, slots=True)
class ResultadoP3:
    """Saida de P3 para um `ano`: media por regiao + gap Sul/Sudeste-Nordeste."""

    ano: int
    media_nordeste: float
    media_sudeste: float
    media_sul: float
    media_sul_sudeste: float
    gap: float
    n_nordeste: int
    n_sudeste: int
    n_sul: int


def calcular_p2(base: pd.DataFrame) -> list[ResultadoP2]:
    """Gap Privada-Publica na media geral, por `ano`, sobre o DF normalizado.

    Mesma definicao de `p2_escola.gap_publica_privada_por_ano`: gap =
    media(Privada) - media(Publica), so com Publica/Privada (Nao informado
    fora do gap, mas contado e reportado).
    """
    df = base.copy()
    df["media_geral"] = _media_geral(df)

    resultados: list[ResultadoP2] = []
    for ano in sorted(df["ano"].unique()):
        sub = df[df["ano"] == ano]
        contagem = (
            sub["tipo_escola"].cat.set_categories(ORDEM_TP_ESCOLA).value_counts().reindex(ORDEM_TP_ESCOLA)
        )

        media_pub = sub.loc[sub["tipo_escola"] == "Publica", "media_geral"].mean()
        media_priv = sub.loc[sub["tipo_escola"] == "Privada", "media_geral"].mean()

        resultados.append(
            ResultadoP2(
                ano=int(ano),
                media_publica=round(float(media_pub), 1),
                media_privada=round(float(media_priv), 1),
                gap=round(float(media_priv - media_pub), 1),
                n_publica=int(contagem.get("Publica", 0)),
                n_privada=int(contagem.get("Privada", 0)),
                n_nao_informado=int(contagem.get("Nao informado", 0)),
            )
        )
    return resultados


def calcular_p3(base: pd.DataFrame) -> list[ResultadoP3]:
    """Disparidade regional (Nordeste vs. Sul/Sudeste) na media geral, por `ano`.

    Mesma ideia de `p3_regiao.gap_bruto`: media geral por regiao, e gap =
    media do bloco Sul+Sudeste (ponderada por N, simples mean sobre as linhas
    do bloco) menos a media do Nordeste.
    """
    df = base.copy()
    df["media_geral"] = _media_geral(df)

    resultados: list[ResultadoP3] = []
    for ano in sorted(df["ano"].unique()):
        sub = df[df["ano"] == ano]
        media_regiao = sub.groupby("regiao", observed=True)["media_geral"].mean()
        n_regiao = sub.groupby("regiao", observed=True)["media_geral"].count()

        nordeste = float(media_regiao.get("Nordeste", float("nan")))
        sudeste = float(media_regiao.get("Sudeste", float("nan")))
        sul = float(media_regiao.get("Sul", float("nan")))

        mask_sul_sudeste = sub["regiao"].isin(["Sul", "Sudeste"])
        media_sul_sudeste = float(sub.loc[mask_sul_sudeste, "media_geral"].mean())

        resultados.append(
            ResultadoP3(
                ano=int(ano),
                media_nordeste=round(nordeste, 1),
                media_sudeste=round(sudeste, 1),
                media_sul=round(sul, 1),
                media_sul_sudeste=round(media_sul_sudeste, 1),
                gap=round(media_sul_sudeste - nordeste, 1),
                n_nordeste=int(n_regiao.get("Nordeste", 0)),
                n_sudeste=int(n_regiao.get("Sudeste", 0)),
                n_sul=int(n_regiao.get("Sul", 0)),
            )
        )
    return resultados


def consolidar(resultados_p2: list[ResultadoP2], resultados_p3: list[ResultadoP3]) -> pd.DataFrame:
    """Empilha P2 e P3 num DataFrame longo (ano, metrica, valor), comparavel
    entre edicoes (cada `ano` ingerido vira um bloco de linhas).

    Colunas: ano, metrica, valor. `metrica` identifica a medida (ex.:
    "p2_media_publica", "p2_gap", "p3_media_nordeste", "p3_gap" etc.).
    """
    linhas: list[dict] = []

    for r in resultados_p2:
        prefixo = "p2_"
        for campo in ("media_publica", "media_privada", "gap", "n_publica", "n_privada", "n_nao_informado"):
            linhas.append({"ano": r.ano, "metrica": prefixo + campo, "valor": getattr(r, campo)})

    for r in resultados_p3:
        prefixo = "p3_"
        for campo in (
            "media_nordeste", "media_sudeste", "media_sul", "media_sul_sudeste",
            "gap", "n_nordeste", "n_sudeste", "n_sul",
        ):
            linhas.append({"ano": r.ano, "metrica": prefixo + campo, "valor": getattr(r, campo)})

    return pd.DataFrame(linhas).sort_values(["ano", "metrica"]).reset_index(drop=True)


def atualizar_consolidado(nrows: int | None = None) -> pd.DataFrame:
    """Recalcula P2/P3 de TODOS os anos mapeados (`modulo_vivo.LAYOUTS`) cujo
    CSV de RESULTADOS exista no disco, e regrava `CAMINHO_PARQUET_VIVO` por
    completo (US-22, criterio 3: ingerir edicao nova so roda esta rotina, sem
    editar codigo). Anos mapeados sem CSV disponivel sao pulados e logados.
    """
    todas_p2: list[ResultadoP2] = []
    todas_p3: list[ResultadoP3] = []

    for ano, layout in sorted(LAYOUTS.items()):
        if not layout.caminho.exists():
            logger.warning(f"[ano={ano}] RESULTADOS nao encontrado em {layout.caminho}; pulando.")
            continue
        base, _divergencias = carregar_edicao_viva(ano, nrows=nrows)
        todas_p2.extend(calcular_p2(base))
        todas_p3.extend(calcular_p3(base))

    consolidada = consolidar(todas_p2, todas_p3)
    CAMINHO_PARQUET_VIVO.parent.mkdir(parents=True, exist_ok=True)
    consolidada.to_parquet(CAMINHO_PARQUET_VIVO, index=False)
    logger.info(f"consolidado gravado em {CAMINHO_PARQUET_VIVO} ({len(consolidada)} linhas).")
    return consolidada


def _validar(ano: int, p2: list[ResultadoP2], p3: list[ResultadoP3], consolidada: pd.DataFrame) -> None:
    """Imprime evidencia de criterios de aceite da US-21 para uma edicao."""
    print(f"\n--- VALIDACAO US-21 — ano {ano} ---")

    print("\nP2 (gap Publica x Privada):")
    for r in p2:
        print(
            f"  ano={r.ano}  media_publica={r.media_publica:.1f} (n={r.n_publica:,})  "
            f"media_privada={r.media_privada:.1f} (n={r.n_privada:,})  "
            f"gap={r.gap:+.1f}  n_nao_informado={r.n_nao_informado:,}"
        )

    print("\nP3 (disparidade regional Nordeste x Sul/Sudeste):")
    for r in p3:
        print(
            f"  ano={r.ano}  Nordeste={r.media_nordeste:.1f} (n={r.n_nordeste:,})  "
            f"Sudeste={r.media_sudeste:.1f} (n={r.n_sudeste:,})  Sul={r.media_sul:.1f} (n={r.n_sul:,})  "
            f"Sul+Sudeste={r.media_sul_sudeste:.1f}  gap={r.gap:+.1f}"
        )

    print("\nsaida consolidada (ano, metrica, valor):")
    print(consolidada.to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="US-21: recalculo de P2/P3 sobre a edicao viva ingerida (EP-07)"
    )
    parser.add_argument("--ano", type=int,
                        help="edicao a carregar (mapeada em modulo_vivo.LAYOUTS)")
    parser.add_argument("--nrows", type=int, default=None,
                        help="amostra (default: arquivo inteiro)")
    parser.add_argument("--atualizar", action="store_true",
                        help="US-22: recalcula TODOS os anos disponiveis e regrava "
                             "o parquet consolidado lido pelo dashboard")
    args = parser.parse_args()

    if args.atualizar:
        consolidada = atualizar_consolidado(nrows=args.nrows)
        print(consolidada.to_string(index=False))
    else:
        if args.ano is None:
            parser.error("--ano e obrigatorio quando --atualizar nao e usado")

        base, divergencias = carregar_edicao_viva(args.ano, nrows=args.nrows)

        p2 = calcular_p2(base)
        p3 = calcular_p3(base)
        consolidada = consolidar(p2, p3)

        _validar(args.ano, p2, p3, consolidada)
