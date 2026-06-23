"""Carga eficiente e tipada dos microdados do ENEM (US-01).

Escopo: SOMENTE leitura tipada e eficiente das edicoes 2022 e 2023 do nucleo
socioeconomico (SES). NAO faz tratamento de nulos, recodificacao nem integracao
entre anos (isso e US-02).

Estrategia de eficiencia (RNF-02):
- `usecols`: le apenas as ~14 colunas relevantes das 76 do CSV.
- `dtype`: categoricas como `category` e notas como `float32` (metade de float64).
- chunking opcional: para validar/medir sem materializar 1,7 GB na RAM.

CSVs do INEP: encoding `latin-1`, separador `;` (confirmado lendo o header real).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes do formato bruto do INEP (confirmadas lendo os CSVs reais)
# ---------------------------------------------------------------------------
ENCODING = "latin-1"
SEPARADOR = ";"

# Raiz do projeto: este arquivo fica em src/enem/carga.py -> sobe 3 niveis.
RAIZ_PROJETO = Path(__file__).resolve().parents[2]

# Layout em disco difere por ano (confirmado): 2022 fica em DADOS/, 2023 na raiz.
CAMINHOS_CSV: dict[int, Path] = {
    2022: RAIZ_PROJETO / "data" / "microdados_enem_2022" / "DADOS" / "MICRODADOS_ENEM_2022.csv",
    2023: RAIZ_PROJETO / "data" / "microdados_enem_2023" / "MICRODADOS_ENEM_2023.csv",
}

# ---------------------------------------------------------------------------
# Colunas relevantes (nucleo SES das perguntas P1-P5) e seus dtypes.
# Origem dos nomes: dicionario INEP + header real dos CSVs.
# - Notas das 5 areas + redacao: float32 (suporta NaN; metade da memoria de float64).
# - Categoricas: `category` (TP_*, Q*, SG_UF_PROVA) — pouca cardinalidade.
# - NU_ANO: int16 (marcador de edicao).
# - NU_INSCRICAO: int64 (chave do candidato; necessaria para integridade/joins futuros).
# ---------------------------------------------------------------------------
DTYPES: dict[str, str] = {
    # Identificacao / marcador
    "NU_INSCRICAO": "int64",
    "NU_ANO": "int16",
    # Notas (US-01: tipadas como float; float32 por eficiencia)
    "NU_NOTA_CN": "float32",
    "NU_NOTA_CH": "float32",
    "NU_NOTA_LC": "float32",
    "NU_NOTA_MT": "float32",
    "NU_NOTA_REDACAO": "float32",
    # Socioeconomicas (categoricas)
    "Q006": "category",   # faixa de renda familiar
    "Q001": "category",   # escolaridade do pai
    "Q002": "category",   # escolaridade da mae
    "TP_ESCOLA": "category",     # tipo de escola (1/2/3)
    "TP_COR_RACA": "category",   # cor/raca (0-6)
    "TP_SEXO": "category",       # F/M
    # Geografia
    "SG_UF_PROVA": "category",   # UF de aplicacao da prova
}

# Ordem de leitura = chaves do mapa de dtypes.
COLUNAS_RELEVANTES: list[str] = list(DTYPES.keys())


def _caminho_edicao(ano: int) -> Path:
    """Devolve o caminho do CSV bruto da edicao, validando existencia."""
    if ano not in CAMINHOS_CSV:
        raise ValueError(f"Ano {ano} nao mapeado. Disponiveis: {sorted(CAMINHOS_CSV)}")
    caminho = CAMINHOS_CSV[ano]
    if not caminho.exists():
        raise FileNotFoundError(f"CSV bruto nao encontrado: {caminho}")
    return caminho


def carregar_edicao(ano: int, nrows: int | None = None) -> pd.DataFrame:
    """Carrega uma edicao do ENEM com selecao de colunas e tipagem.

    Le apenas `COLUNAS_RELEVANTES` aplicando `DTYPES`. Eficiente em memoria
    (usecols + dtype). Use `nrows` para amostra (validacao rapida sem ler tudo).

    Args:
        ano: edicao (2022 ou 2023).
        nrows: se informado, le apenas as N primeiras linhas (amostra).

    Returns:
        DataFrame tipado, somente com as colunas relevantes.
    """
    caminho = _caminho_edicao(ano)
    return pd.read_csv(
        caminho,
        sep=SEPARADOR,
        encoding=ENCODING,
        usecols=COLUNAS_RELEVANTES,
        dtype=DTYPES,
        nrows=nrows,
    )


def contar_linhas(ano: int) -> int:
    """Conta as linhas de dados da edicao por streaming (sem carregar na RAM).

    Le o arquivo em blocos de bytes e conta quebras de linha; subtrai 1 do
    header. Permite validar a contagem total mesmo sem caber a base em memoria.
    """
    caminho = _caminho_edicao(ano)
    total = 0
    with open(caminho, "rb") as f:
        while bloco := f.read(1024 * 1024):
            total += bloco.count(b"\n")
    return total - 1  # desconta o header


def medir_memoria(ano: int, chunksize: int = 500_000) -> dict:
    """Le a edicao INTEIRA via chunking e mede memoria sem materializar tudo.

    Soma o consumo de memoria por chunk (deep) e a contagem de linhas. Como cada
    chunk e descartado apos a medicao, a RAM de pico fica limitada a ~1 chunk —
    isso e o que torna a leitura viavel em maquina comum (RNF-02).

    Args:
        ano: edicao a medir.
        chunksize: linhas por bloco.

    Returns:
        dict com linhas, memoria_mb (soma dos chunks, deep), dtypes e n_colunas.
    """
    caminho = _caminho_edicao(ano)
    leitor = pd.read_csv(
        caminho,
        sep=SEPARADOR,
        encoding=ENCODING,
        usecols=COLUNAS_RELEVANTES,
        dtype=DTYPES,
        chunksize=chunksize,
    )
    total_linhas = 0
    total_bytes = 0
    dtypes_obs: dict[str, str] = {}
    for chunk in leitor:
        total_linhas += len(chunk)
        total_bytes += int(chunk.memory_usage(deep=True).sum())
        dtypes_obs = {c: str(t) for c, t in chunk.dtypes.items()}
    return {
        "ano": ano,
        "linhas": total_linhas,
        "memoria_mb": round(total_bytes / 1024**2, 1),
        "n_colunas": len(dtypes_obs),
        "dtypes": dtypes_obs,
    }


if __name__ == "__main__":
    # Validacao executavel da US-01: mede memoria e tipos das duas edicoes
    # via chunking (cabe em maquina comum). Saida = evidencia dos criterios.
    for ano in sorted(CAMINHOS_CSV):
        print(f"\n=== ENEM {ano} ===")
        info = medir_memoria(ano)
        print(f"linhas: {info['linhas']:,}")
        print(f"colunas: {info['n_colunas']}")
        print(f"memoria (base inteira, tipada, deep): {info['memoria_mb']} MB")
        print("dtypes:")
        for col, tipo in info["dtypes"].items():
            print(f"  {col:<16} {tipo}")
