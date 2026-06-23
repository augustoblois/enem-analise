"""Modulo vivo: carregador de edicao parametrizavel por ano (US-20, EP-07).

Escopo (SO US-20): ler o CSV de RESULTADOS de qualquer edicao mapeada e
normalizar para um schema-alvo comum, restrito aos eixos que SOBREVIVEM a
quebra de linkage 2024 (US-17/US-18): escola x nota (P2) e regiao x nota (P3).
NAO calcula P2/P3 (isso e US-21) e NAO toca no dashboard (US-22).

ISOLAMENTO DO NUCLEO SES (RNF-07): este modulo tem entrada propria
(`carregar_edicao_viva`) e NAO importa `carga.py`/`tratamento.py` nem
`carregar_edicao`/`tratar_edicao`/`construir_base` de la. A base SES tratada
(2022+2023, parquet de `tratamento.py`) nunca e lida nem reprocessada aqui.
A unica coisa reaproveitada de outro modulo do projeto e a CONSTANTE estatica
`MAPA_UF_REGIAO` (e `ORDEM_REGIAO`) de `eda.py` — e so uma tabela fixa
UF->macrorregiao do IBGE, sem nenhuma dependencia da base SES tratada.

------------------------------------------------------------------------------
LAYOUT POR EDICAO (mapeamento de US-20, criterio 1)
------------------------------------------------------------------------------
- 2022: base UNICA (PARTICIPANTES+RESULTADOS juntos no mesmo CSV).
  data/microdados_enem_2022/DADOS/MICRODADOS_ENEM_2022.csv; latin-1; sep ';'.
  Escola: TP_ESCOLA (1=Nao respondeu, 2=Publica, 3=Privada).
- 2023: base UNICA, mesmo layout logico de 2022.
  data/microdados_enem_2023/MICRODADOS_ENEM_2023.csv; latin-1; sep ';'.
  Escola: TP_ESCOLA (1=Nao respondeu, 2=Publica, 3=Privada).
- 2024: layout NOVO — TRES CSVs separados em DADOS/ (PARTICIPANTES, ITENS_PROVA,
  RESULTADOS), confirmado lendo o diretorio real. Para os eixos P2/P3 o
  RESULTADOS_2024.csv basta: ja trai CO_ESCOLA, SG_UF_ESC, TP_DEPENDENCIA_ADM_ESC,
  SG_UF_PROVA e as 5 notas na MESMA linha (nao precisa juntar com PARTICIPANTES).
  data/microdados_enem_2024/DADOS/RESULTADOS_2024.csv; latin-1; sep ';'.
  Escola: TP_DEPENDENCIA_ADM_ESC (1=Federal, 2=Estadual, 3=Municipal, 4=Privada)
  — DOMINIO DIFERENTE de TP_ESCOLA (ver divergencia abaixo).

------------------------------------------------------------------------------
DIVERGENCIA DE HEADER/CODIFICACAO DE ESCOLA — 2024 vs 2022-2023 (criterio 4)
------------------------------------------------------------------------------
1. Nome da coluna muda: TP_ESCOLA (2022-2023) -> TP_DEPENDENCIA_ADM_ESC (2024).
2. Dominio de codigos muda E NAO E COMPATIVEL por simples renome:
   - 2022-2023 {1,2,3} = {Nao respondeu, Publica, Privada} (dependencia
     administrativa NAO detalhada: rede publica unica, sem unica de
     Federal/Estadual/Municipal).
   - 2024 {1,2,3,4} = {Federal, Estadual, Municipal, Privada} (rede publica
     DETALHADA em 3 niveis administrativos; NAO ha codigo "Nao informado").
3. Normalizacao adotada aqui: Federal+Estadual+Municipal -> "Publica";
   4 -> "Privada". Resultado fica comparavel a 2022-2023 em 2 categorias
   (Publica/Privada), mas a granularidade administrativa de 2024 e perdida
   na normalizacao (registrada, nao descartada silenciosamente: ver
   `divergencias_detectadas` no retorno de `carregar_edicao_viva`).
4. 2024 nao tem categoria "Nao informado" equivalente — quem nao tem escola
   registrada vem como NaN em CO_ESCOLA/TP_DEPENDENCIA_ADM_ESC (treineiros,
   eliminados antes do preenchimento). Mapeado para "Nao informado" tambem,
   por NaN explicito (nao confundido com Publica/Privada).
5. UF: 2022-2023 usa SG_UF_PROVA (UF de aplicacao da prova) como unica fonte
   de geografia no eixo P3. 2024 tambem trai SG_UF_PROVA no RESULTADOS (alem de
   SG_UF_ESC, que NAO usamos aqui para manter P3 consistente entre edicoes:
   regiao = UF da PROVA, nao da escola, nas tres edicoes).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Raiz do projeto: este arquivo fica em src/enem/modulo_vivo.py -> sobe 3 niveis.
RAIZ_PROJETO = Path(__file__).resolve().parents[2]

# Formato bruto do INEP (mesmas constantes do nucleo SES, sao so o encoding/
# separador dos CSVs do INEP — fato do formato, nao dependencia de logica SES).
ENCODING = "latin-1"
SEPARADOR = ";"

# Macrorregiao por UF (tabela fixa IBGE, reaproveitada de eda.py por ser
# constante estatica, sem qualquer dependencia da base SES tratada).
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

NOTAS_ALVO = ["nota_cn", "nota_ch", "nota_lc", "nota_mt", "nota_redacao"]
SCHEMA_ALVO = ["ano", "uf", "regiao", "tipo_escola", *NOTAS_ALVO]


@dataclass(frozen=True, slots=True)
class LayoutEdicao:
    """Descreve o layout de leitura do RESULTADOS de uma edicao especifica."""

    caminho: Path
    coluna_escola: str
    mapa_escola: dict[str, str]
    coluna_uf: str = "SG_UF_PROVA"
    colunas_notas: tuple[str, str, str, str, str] = (
        "NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO",
    )


# Dominios de tipo de escola por edicao (criterio 1 + 4: mapeamento e divergencia).
MAPA_TP_ESCOLA_2022_2023: dict[str, str] = {
    "1": "Nao informado",
    "2": "Publica",
    "3": "Privada",
}
MAPA_TP_DEPENDENCIA_ADM_ESC_2024: dict[str, str] = {
    "1": "Publica",   # Federal
    "2": "Publica",   # Estadual
    "3": "Publica",   # Municipal
    "4": "Privada",
}

LAYOUTS: dict[int, LayoutEdicao] = {
    2022: LayoutEdicao(
        caminho=RAIZ_PROJETO / "data" / "microdados_enem_2022" / "DADOS" / "MICRODADOS_ENEM_2022.csv",
        coluna_escola="TP_ESCOLA",
        mapa_escola=MAPA_TP_ESCOLA_2022_2023,
    ),
    2023: LayoutEdicao(
        caminho=RAIZ_PROJETO / "data" / "microdados_enem_2023" / "MICRODADOS_ENEM_2023.csv",
        coluna_escola="TP_ESCOLA",
        mapa_escola=MAPA_TP_ESCOLA_2022_2023,
    ),
    2024: LayoutEdicao(
        caminho=RAIZ_PROJETO / "data" / "microdados_enem_2024" / "DADOS" / "RESULTADOS_2024.csv",
        coluna_escola="TP_DEPENDENCIA_ADM_ESC",
        mapa_escola=MAPA_TP_DEPENDENCIA_ADM_ESC_2024,
    ),
}

ORDEM_TP_ESCOLA = ["Publica", "Privada", "Nao informado"]


def _dtypes_leitura(layout: LayoutEdicao) -> dict[str, str]:
    """Dtypes eficientes (RNF-02) para as colunas que o layout da edicao usa."""
    dtypes: dict[str, str] = {
        layout.coluna_escola: "category",
        layout.coluna_uf: "category",
    }
    for col in layout.colunas_notas:
        dtypes[col] = "float32"
    return dtypes


def _layout_edicao(ano: int) -> LayoutEdicao:
    if ano not in LAYOUTS:
        raise ValueError(f"Ano {ano} nao mapeado no modulo vivo. Disponiveis: {sorted(LAYOUTS)}")
    layout = LAYOUTS[ano]
    if not layout.caminho.exists():
        raise FileNotFoundError(f"RESULTADOS da edicao {ano} nao encontrado: {layout.caminho}")
    return layout


def _detectar_divergencias(ano: int, layout: LayoutEdicao, colunas_lidas: list[str]) -> list[str]:
    """Compara o layout da edicao ao layout-referencia (2022/2023) e LOGA cada
    divergencia explicitamente (criterio 4 da US-20: nao silenciar).
    """
    divergencias: list[str] = []
    layout_ref = LAYOUTS[2022]

    if layout.coluna_escola != layout_ref.coluna_escola:
        msg = (
            f"[ano={ano}] coluna de tipo de escola difere do layout-referencia: "
            f"'{layout.coluna_escola}' (esperado nas edicoes 2022/2023: "
            f"'{layout_ref.coluna_escola}')."
        )
        divergencias.append(msg)
        logger.warning(msg)

    if layout.mapa_escola != layout_ref.mapa_escola:
        msg = (
            f"[ano={ano}] dominio de codigos de tipo de escola difere do "
            f"layout-referencia: {sorted(layout.mapa_escola.items())} (esperado: "
            f"{sorted(layout_ref.mapa_escola.items())}). Normalizado para "
            f"{ORDEM_TP_ESCOLA} via mapa proprio da edicao; granularidade "
            f"administrativa original (se houver) e perdida na normalizacao."
        )
        divergencias.append(msg)
        logger.warning(msg)

    return divergencias


def carregar_edicao_viva(
    ano: int, nrows: int | None = None
) -> tuple[pd.DataFrame, list[str]]:
    """Le o RESULTADOS de `ano` e normaliza para o SCHEMA_ALVO comum.

    Entrada propria do modulo vivo: NAO usa `carga.carregar_edicao` nem
    `tratamento.tratar_edicao`. Le apenas as colunas necessarias para os eixos
    P2 (escola x nota) e P3 (regiao x nota), com `usecols`/`dtype` (RNF-02).

    Args:
        ano: edicao mapeada em `LAYOUTS` (2022, 2023 ou 2024).
        nrows: se informado, le so as N primeiras linhas (amostra).

    Returns:
        Tupla (DataFrame no SCHEMA_ALVO, lista de divergencias detectadas).
    """
    layout = _layout_edicao(ano)
    colunas = [layout.coluna_escola, layout.coluna_uf, *layout.colunas_notas]
    dtypes = _dtypes_leitura(layout)

    divergencias = _detectar_divergencias(ano, layout, colunas)

    bruto = pd.read_csv(
        layout.caminho,
        sep=SEPARADOR,
        encoding=ENCODING,
        usecols=colunas,
        dtype=dtypes,
        nrows=nrows,
    )

    notas_cn, notas_ch, notas_lc, notas_mt, notas_redacao = layout.colunas_notas

    tipo_escola = pd.Categorical(
        bruto[layout.coluna_escola].astype("string").map(layout.mapa_escola),
        categories=ORDEM_TP_ESCOLA,
        ordered=False,
    )
    if tipo_escola.isna().any():
        n_nao_mapeado = int(pd.isna(tipo_escola).sum())
        logger.warning(
            f"[ano={ano}] {n_nao_mapeado} linhas com codigo de escola fora do "
            f"mapa conhecido ou NaN; tratadas como 'Nao informado'."
        )
        tipo_escola = tipo_escola.fillna("Nao informado")

    uf = bruto[layout.coluna_uf].astype("string")
    regiao_mapeada = uf.map(MAPA_UF_REGIAO)
    n_uf_fora_mapa = int(regiao_mapeada.isna().sum())
    if n_uf_fora_mapa:
        msg = f"[ano={ano}] {n_uf_fora_mapa} linhas com UF fora do mapa de regioes conhecido."
        divergencias.append(msg)
        logger.warning(msg)

    normalizado = pd.DataFrame(
        {
            "ano": pd.array([ano] * len(bruto), dtype="int16"),
            "uf": pd.Categorical(uf),
            "regiao": pd.Categorical(regiao_mapeada, categories=ORDEM_REGIAO, ordered=False),
            "tipo_escola": tipo_escola,
            "nota_cn": bruto[notas_cn].astype("float32"),
            "nota_ch": bruto[notas_ch].astype("float32"),
            "nota_lc": bruto[notas_lc].astype("float32"),
            "nota_mt": bruto[notas_mt].astype("float32"),
            "nota_redacao": bruto[notas_redacao].astype("float32"),
        }
    )
    return normalizado[SCHEMA_ALVO], divergencias


def _validar(ano: int, base: pd.DataFrame, divergencias: list[str]) -> None:
    """Imprime evidencia de criterios de aceite da US-20 para uma edicao."""
    print(f"\n--- VALIDACAO US-20 — ano {ano} ---")
    print("shape:", base.shape)
    print("\ndtypes:")
    for c, t in base.dtypes.items():
        print(f"  {c:<14} {t}")
    print("\nschema-alvo:", list(base.columns))
    print("\namostra:")
    print(base.head(5).to_string())
    print("\ntipo_escola (contagem):")
    print(base["tipo_escola"].value_counts(dropna=False).to_string())
    print("\nregiao (contagem):")
    print(base["regiao"].value_counts(dropna=False).to_string())
    print("\ndivergencias detectadas:")
    if divergencias:
        for d in divergencias:
            print(f"  - {d}")
    else:
        print("  (nenhuma — layout igual ao de referencia 2022/2023)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="US-20: carregador de edicao viva (EP-07), parametrizavel por ano"
    )
    parser.add_argument("--ano", type=int, required=True, choices=sorted(LAYOUTS),
                        help="edicao a carregar")
    parser.add_argument("--nrows", type=int, default=None,
                        help="amostra (default: arquivo inteiro)")
    args = parser.parse_args()

    base, divergencias = carregar_edicao_viva(args.ano, nrows=args.nrows)
    _validar(args.ano, base, divergencias)
