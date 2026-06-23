"""Tratamento, recodificacao e integracao das edicoes 2022+2023 (US-02).

Escopo (SO US-02): partir das bases tipadas da US-01 (`carga.carregar_edicao`),
tratar nulos por regra documentada, recodificar as variaveis socioeconomicas
para rotulos legiveis e ESTAVEIS entre edicoes, concatenar 2022+2023 com coluna
`ano` e persistir a base unificada em parquet (fora do versionamento, RNF-04).

NAO faz EDA (US-04), nem dicionario formal (US-03), nem modelagem.

------------------------------------------------------------------------------
DECISOES DE TRATAMENTO DE NULOS (por variavel) — insumo da US-03
------------------------------------------------------------------------------
- Notas (NU_NOTA_*): NaN MANTIDO. NaN aqui e legitimo (ausente/eliminado nao tem
  nota). Imputar distorceria distribuicoes e medias das perguntas P1-P5. ~24-28%
  por area, consistente entre 2022 e 2023.
- Q006 / Q001 / Q002: o INEP NAO deixa em branco — quem nao informa recebe um
  codigo proprio dentro do dominio ("Nenhuma Renda" em Q006 = letra A; "Nao sei"
  em Q001/Q002 = letra H). Verificado: 0 NaN nos CSVs. Logo nao ha imputacao;
  apenas tornamos o "Nao sei" (H) explicito como categoria separada da escala.
- TP_ESCOLA: codigo 1 = "Nao Respondeu" (carrega os nulos de tipo de escola).
  Verificado: 0 NaN, mas grande massa em "1". Recodificado para "Nao informado"
  como categoria EXPLICITA — nao e dropado nem misturado a publica/privada.

------------------------------------------------------------------------------
COMPARABILIDADE 2022 vs 2023 (validada contra os dicionarios INEP) — risco PRD
------------------------------------------------------------------------------
- TP_ESCOLA: codigos {1,2,3} e rotulos IDENTICOS nos dois anos. Comparavel direto.
- Q001 / Q002: codigos {A..H} e rotulos IDENTICOS nos dois anos. Comparavel direto.
- Q006: os codigos {A..Q} e a ORDEM ordinal sao IDENTICOS, MAS as faixas em R$
  MUDARAM (2022 ancora no salario minimo R$ 1.212; 2023 em R$ 1.320 — as bordas
  de cada faixa deslocam). Os rotulos em REAIS NAO sao comparaveis entre anos.
  O que e estavel e a posicao ordinal de cada letra em SALARIOS MINIMOS (a faixa
  B sempre = "ate 1 SM", C/D = "1-2 SM", etc.). => Recodificamos Q006 pela faixa
  em salarios minimos (estavel entre edicoes), NAO pelos valores absolutos em R$.
  Assim a concatenacao 2022+2023 nao mistura escalas monetarias diferentes.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .carga import RAIZ_PROJETO, carregar_edicao

# ---------------------------------------------------------------------------
# Destino do parquet: pasta de artefatos sob data/ (ja ignorada pelo git, RNF-04).
# ---------------------------------------------------------------------------
DIR_PROCESSADO = RAIZ_PROJETO / "data" / "processado"
CAMINHO_PARQUET = DIR_PROCESSADO / "enem_2022_2023.parquet"

# ---------------------------------------------------------------------------
# Mapas de recodificacao (origem: dicionarios INEP 2022 e 2023, conferidos).
# ---------------------------------------------------------------------------

# TP_ESCOLA — identico nos dois anos. "1" carrega os nao-respondentes.
MAPA_TP_ESCOLA: dict[str, str] = {
    "1": "Nao informado",
    "2": "Publica",
    "3": "Privada",
}
ORDEM_TP_ESCOLA = ["Publica", "Privada", "Nao informado"]

# Q001 / Q002 — escolaridade dos pais. Codigos {A..H} identicos nos dois anos.
# A..G sao ordinais (do menor ao maior); H ("Nao sei") fica FORA da escala.
MAPA_ESCOLARIDADE: dict[str, str] = {
    "A": "Nunca estudou",
    "B": "Fundamental I incompleto",
    "C": "Fundamental I completo",
    "D": "Fundamental II completo",
    "E": "Medio completo",
    "F": "Superior completo",
    "G": "Pos-graduacao",
    "H": "Nao sei",
}
# Ordem ordinal: escala A->G crescente; "Nao sei" ao final (nao ordenavel).
ORDEM_ESCOLARIDADE = [
    "Nunca estudou",
    "Fundamental I incompleto",
    "Fundamental I completo",
    "Fundamental II completo",
    "Medio completo",
    "Superior completo",
    "Pos-graduacao",
    "Nao sei",
]

# Q006 — renda. Codigos {A..Q} e ordem identicos nos dois anos; faixas em R$
# diferem entre edicoes. Recodificamos pela faixa em SALARIOS MINIMOS (SM),
# que e estavel entre 2022 e 2023 (mesma letra = mesma faixa em SM).
# A=sem renda; B=ate 1 SM; C-D=1-2 SM; E-G=2-4 SM; H-J=4-6 SM (aprox);
# Mapeamento conservador por blocos ordinais comparaveis entre anos.
MAPA_Q006: dict[str, str] = {
    "A": "Sem renda",
    "B": "Ate 1 SM",
    "C": "1 a 2 SM",
    "D": "1 a 2 SM",
    "E": "2 a 3 SM",
    "F": "2 a 3 SM",
    "G": "3 a 4 SM",
    "H": "4 a 5 SM",
    "I": "5 a 6 SM",
    "J": "6 a 7 SM",
    "K": "7 a 8 SM",
    "L": "8 a 9 SM",
    "M": "9 a 10 SM",
    "N": "10 a 12 SM",
    "O": "12 a 15 SM",
    "P": "15 a 20 SM",
    "Q": "Acima de 20 SM",
}
ORDEM_Q006 = [
    "Sem renda",
    "Ate 1 SM",
    "1 a 2 SM",
    "2 a 3 SM",
    "3 a 4 SM",
    "4 a 5 SM",
    "5 a 6 SM",
    "6 a 7 SM",
    "7 a 8 SM",
    "8 a 9 SM",
    "9 a 10 SM",
    "10 a 12 SM",
    "12 a 15 SM",
    "15 a 20 SM",
    "Acima de 20 SM",
]

ANOS = (2022, 2023)


def _recodificar(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica recodificacoes ordinais/legiveis sobre uma edicao ja carregada.

    Cria colunas novas (com sufixo de significado) e mantem ordem ordinal via
    `pd.Categorical(ordered=True)` para preservar a semantica nas analises P1-P5.
    As colunas originais (Q006/Q001/Q002/TP_ESCOLA) sao removidas apos recodificar.
    """
    out = df.copy()

    out["tipo_escola"] = pd.Categorical(
        out["TP_ESCOLA"].astype("string").map(MAPA_TP_ESCOLA),
        categories=ORDEM_TP_ESCOLA,
        ordered=False,  # tipo de escola nao e ordinal
    )
    out["escolaridade_pai"] = pd.Categorical(
        out["Q001"].astype("string").map(MAPA_ESCOLARIDADE),
        categories=ORDEM_ESCOLARIDADE,
        ordered=True,
    )
    out["escolaridade_mae"] = pd.Categorical(
        out["Q002"].astype("string").map(MAPA_ESCOLARIDADE),
        categories=ORDEM_ESCOLARIDADE,
        ordered=True,
    )
    out["faixa_renda"] = pd.Categorical(
        out["Q006"].astype("string").map(MAPA_Q006),
        categories=ORDEM_Q006,
        ordered=True,
    )

    return out.drop(columns=["TP_ESCOLA", "Q001", "Q002", "Q006"])


def tratar_edicao(ano: int, nrows: int | None = None) -> pd.DataFrame:
    """Carrega (US-01) + trata nulos + recodifica uma edicao, com coluna `ano`.

    Nulos: notas mantem NaN (legitimo); SES nao tem NaN (verificado), o "nao
    informado"/"nao sei" vira categoria explicita na recodificacao.

    Args:
        ano: 2022 ou 2023.
        nrows: amostra opcional para validacao rapida.
    """
    df = carregar_edicao(ano, nrows=nrows)
    df = _recodificar(df)
    df["ano"] = pd.Categorical([ano] * len(df), categories=list(ANOS), ordered=True)
    return df


def construir_base(nrows: int | None = None) -> pd.DataFrame:
    """Concatena 2022+2023 tratadas numa unica base analitica com coluna `ano`.

    Concatena SO apos a recodificacao para faixas estaveis entre edicoes — assim
    nenhuma escala divergente (ex.: R$ de Q006) e misturada silenciosamente.
    """
    partes = [tratar_edicao(ano, nrows=nrows) for ano in ANOS]
    base = pd.concat(partes, ignore_index=True)
    return base


def persistir(base: pd.DataFrame, caminho: Path = CAMINHO_PARQUET) -> Path:
    """Grava a base unificada em parquet (eficiente, preserva dtypes/category).

    Destino sob data/processado/ — pasta ignorada pelo git (RNF-04).
    """
    caminho.parent.mkdir(parents=True, exist_ok=True)
    base.to_parquet(caminho, engine="pyarrow", index=False)
    return caminho


def _validar(base: pd.DataFrame) -> None:
    """Imprime evidencia de cada criterio de aceite da US-02."""
    print("\n--- VALIDACAO US-02 ---")
    print("linhas totais:", f"{len(base):,}")
    print("\ncontagem por ano:")
    print(base["ano"].value_counts().sort_index().to_string())

    print("\ndtypes:")
    for c, t in base.dtypes.items():
        print(f"  {c:<18} {t}")

    print("\nfaixa_renda (ordinal) por ano:")
    print(pd.crosstab(base["faixa_renda"], base["ano"]).to_string())

    print("\ntipo_escola por ano:")
    print(pd.crosstab(base["tipo_escola"], base["ano"]).to_string())

    print("\nescolaridade_mae por ano:")
    print(pd.crosstab(base["escolaridade_mae"], base["ano"]).to_string())

    print("\nNaN em notas (deve persistir — legitimo):")
    notas = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
    print(base[notas].isna().sum().to_string())

    print("\nNaN nas recodificacoes SES (deve ser 0 — sem perda):")
    ses = ["faixa_renda", "tipo_escola", "escolaridade_pai", "escolaridade_mae"]
    print(base[ses].isna().sum().to_string())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="US-02: tratamento + integracao 2022+2023")
    parser.add_argument("--nrows", type=int, default=None,
                        help="amostra por edicao (default: base inteira)")
    args = parser.parse_args()

    base = construir_base(nrows=args.nrows)
    _validar(base)
    destino = persistir(base)
    tam_mb = round(destino.stat().st_size / 1024**2, 1)
    print(f"\nparquet gravado: {destino} ({tam_mb} MB)")
