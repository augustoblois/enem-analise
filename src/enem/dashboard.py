"""Dashboard Streamlit interativo sobre a base tratada 2022+2023 (US-15).

Escopo: SO leitura do parquet tratado (US-02) + filtros reativos + visualizacoes
Plotly. Reusa a logica de agregacao de P1/P2/P3 (eda.py), nao reinventa regra de
negocio. NAO recodifica, NAO reprocessa CSV bruto.

NOTA DE IMPORT: `streamlit run src/enem/dashboard.py` executa este arquivo como
script solto (nao como pacote) — import relativo (`from .tratamento import`)
quebraria com "attempted relative import with no known parent package". Por
isso inserimos a raiz do repo em `sys.path` e usamos import ABSOLUTO
(`from src.enem...`), o que permite rodar tanto via `streamlit run` quanto via
`python -m src.enem.dashboard`.

DECISOES (herdadas de tratamento.py/eda.py, ver CLAUDE.md):
- Notas mantem NaN; medias usam skipna (`media_geral_notas`).
- faixa_renda/tipo_escola sao ordinais — eixos seguem ORDEM_Q006/ORDEM_TP_ESCOLA,
  nunca ordem alfabetica.
- "Nao informado" em tipo_escola e categoria explicita, presente no filtro.
- Regiao deriva de SG_UF_PROVA via MAPA_UF_REGIAO (decisao de analise, eda.py).
- O filtro de ano deriva de `base["ano"].unique()` (nunca hardcode
  [2022, 2023]) para comportar edicoes futuras (P2/P3 via EP-07) sem quebrar.

US-22 (integracao do modulo vivo P2/P3, EP-07):
- O dashboard SO LE o parquet consolidado de `modulo_vivo_metricas`
  (`CAMINHO_PARQUET_VIVO`) via `carregar_metricas_vivas` — nunca importa
  `modulo_vivo`/`carregar_edicao_viva` nem recalcula on-demand. Atualizar para
  uma edicao nova (ex. 2025) e rodar `python -m src.enem.modulo_vivo_metricas
  --atualizar` (ver docstring daquele modulo); o dashboard so reflete o
  parquet regravado, sem mudanca de codigo.
- ISOLAMENTO SES (RNF-07, achado do teto temporal 2023): anos vivos (ex. 2024)
  SO aparecem nas abas Escola (P2) e Regiao (P3), ao lado de 2022/2023. As
  visoes SES (Distribuicao de notas, Renda P1, Mapa & Correlacao, KPIs de
  topo) filtram SEMPRE para `anos_disponiveis` (anos do parquet SES), mesmo
  que o usuario marque um ano vivo no multiselect — escolha deliberada para
  manter o multiselect unico na sidebar (UX simples) sem deixar o ano vivo
  contaminar SES por engano.
- Se o parquet vivo nao existir ainda (rotina US-22 nunca rodada), as abas
  P2/P3 mostram so 2022/2023 (SES) com aviso — dashboard NUNCA quebra por
  falta do artefato vivo, que e opcional/incremental.


US-16 (mapa + correlacao renda x nota):
- Malha de UF versionada em `assets/geo/br_uf.geojson` (NAO em data/, que e
  gitignored); `featureidkey="properties.sigla"` casa com `SG_UF_PROVA`.
- O mapa coropletico IGNORA o filtro de UF (mostra as 27 UFs sempre) — filtrar
  por UF e mostrar so 1-2 estados no mapa nao agrega leitura; em vez disso a(s)
  UF(s) selecionada(s) sao DESTACADAS com contorno proprio.
- Correlacao usa Spearman (rho), nao Pearson — `faixa_renda` e ordinal, mesma
  logica de p1_renda.estatistica_suporte (rank ordinal x media geral).
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from src.enem.eda import MAPA_UF_REGIAO, NOTAS, ORDEM_REGIAO, ROTULO_NOTA, media_geral_notas
from src.enem.modulo_vivo_metricas import CAMINHO_PARQUET_VIVO
from src.enem.tratamento import CAMINHO_PARQUET, ORDEM_Q006, ORDEM_TP_ESCOLA

CAMINHO_GEOJSON_UF = RAIZ_PROJETO / "assets" / "geo" / "br_uf.geojson"

st.set_page_config(page_title="ENEM 2022+2023 — Desigualdade x Desempenho", layout="wide")


@st.cache_data
def carregar_geojson_uf() -> dict:
    """Le a malha de UF do Brasil (US-16), versionada em assets/geo/."""
    if not CAMINHO_GEOJSON_UF.exists():
        raise FileNotFoundError(f"GeoJSON de UF nao encontrado: {CAMINHO_GEOJSON_UF}")
    with open(CAMINHO_GEOJSON_UF, encoding="utf-8") as arquivo:
        return json.load(arquivo)


@st.cache_data
def carregar_base() -> pd.DataFrame:
    """Le o parquet tratado (US-02) uma unica vez por sessao de processo."""
    if not CAMINHO_PARQUET.exists():
        raise FileNotFoundError(f"Parquet tratado nao encontrado: {CAMINHO_PARQUET}")
    base = pd.read_parquet(CAMINHO_PARQUET)
    base["regiao"] = pd.Categorical(
        base["SG_UF_PROVA"].astype(str).map(MAPA_UF_REGIAO),
        categories=ORDEM_REGIAO,
        ordered=False,
    )
    base["media_geral"] = media_geral_notas(base)
    return base


@st.cache_data
def carregar_metricas_vivas() -> pd.DataFrame:
    """Le o parquet consolidado de P2/P3 do modulo vivo (US-21/US-22), se
    existir. Retorna DataFrame vazio (colunas ano/metrica/valor) quando o
    artefato ainda nao foi gerado — a rotina e `python -m
    src.enem.modulo_vivo_metricas --atualizar` (ver docstring do modulo).
    """
    if not CAMINHO_PARQUET_VIVO.exists():
        return pd.DataFrame(columns=["ano", "metrica", "valor"])
    return pd.read_parquet(CAMINHO_PARQUET_VIVO)


def tabela_p2_viva(metricas_vivas: pd.DataFrame) -> pd.DataFrame:
    """Pivota o consolidado (ano, metrica, valor) para o formato longo usado
    no grafico de P2 (tipo_escola, ano, media_geral), so com os anos vivos.
    """
    if metricas_vivas.empty:
        return pd.DataFrame(columns=["tipo_escola", "ano", "media_geral"])
    linhas = []
    for ano, grupo in metricas_vivas.groupby("ano"):
        valores = grupo.set_index("metrica")["valor"]
        linhas.append({"tipo_escola": "Publica", "ano": ano, "media_geral": valores.get("p2_media_publica")})
        linhas.append({"tipo_escola": "Privada", "ano": ano, "media_geral": valores.get("p2_media_privada")})
    return pd.DataFrame(linhas).dropna(subset=["media_geral"])


def tabela_p3_viva(metricas_vivas: pd.DataFrame) -> pd.DataFrame:
    """Pivota o consolidado (ano, metrica, valor) para o formato longo usado
    no grafico de P3 (regiao, ano, media_geral), so com os anos vivos.
    """
    if metricas_vivas.empty:
        return pd.DataFrame(columns=["regiao", "ano", "media_geral"])
    campo_regiao = {
        "p3_media_nordeste": "Nordeste",
        "p3_media_sudeste": "Sudeste",
        "p3_media_sul": "Sul",
    }
    linhas = []
    for ano, grupo in metricas_vivas.groupby("ano"):
        valores = grupo.set_index("metrica")["valor"]
        for metrica, regiao in campo_regiao.items():
            if metrica in valores.index:
                linhas.append({"regiao": regiao, "ano": ano, "media_geral": valores[metrica]})
    return pd.DataFrame(linhas).dropna(subset=["media_geral"])


def aplicar_filtros(
    base: pd.DataFrame,
    anos: list,
    ufs: list[str],
    tipos_escola: list[str],
    faixas_renda: list[str],
) -> pd.DataFrame:
    """Filtra a base pelos valores escolhidos na sidebar; listas vazias = sem filtro."""
    filtrada = base
    if anos:
        filtrada = filtrada[filtrada["ano"].isin(anos)]
    if ufs:
        filtrada = filtrada[filtrada["SG_UF_PROVA"].isin(ufs)]
    if tipos_escola:
        filtrada = filtrada[filtrada["tipo_escola"].isin(tipos_escola)]
    if faixas_renda:
        filtrada = filtrada[filtrada["faixa_renda"].isin(faixas_renda)]
    return filtrada


base_completa = carregar_base()
anos_disponiveis = sorted(int(a) for a in base_completa["ano"].unique())

metricas_vivas_completas = carregar_metricas_vivas()
anos_vivos_disponiveis = sorted(set(metricas_vivas_completas["ano"]) - set(anos_disponiveis))
anos_filtro_opcoes = anos_disponiveis + anos_vivos_disponiveis

st.sidebar.title("Filtros")
filtro_ano = st.sidebar.multiselect("Ano", options=anos_filtro_opcoes, default=anos_filtro_opcoes)
if anos_vivos_disponiveis:
    st.sidebar.caption(
        f"Anos vivos ({', '.join(str(a) for a in anos_vivos_disponiveis)}) so entram "
        "nas abas Escola (P2) e Regiao (P3) — o nucleo SES (renda, mapa, KPIs) so "
        "tem linkage perfil-nota em 2022/2023 (ver achado de governanca, CLAUDE.md)."
    )
filtro_uf = st.sidebar.multiselect(
    "UF da prova", options=sorted(base_completa["SG_UF_PROVA"].dropna().unique())
)
filtro_escola = st.sidebar.multiselect(
    "Tipo de escola", options=ORDEM_TP_ESCOLA, default=ORDEM_TP_ESCOLA
)
filtro_renda = st.sidebar.multiselect("Faixa de renda", options=ORDEM_Q006)

# Isolamento SES (RNF-07, US-22): visoes do nucleo SES SEMPRE restringem o ano
# aos anos do parquet SES (`anos_disponiveis`), ignorando anos vivos mesmo se
# selecionados no multiselect — o linkage perfil-nota nao existe fora de
# 2022/2023 (achado do teto temporal). Abas P2/P3 usam `filtro_ano` cru.
filtro_ano_ses = [a for a in filtro_ano if a in anos_disponiveis]
base = aplicar_filtros(base_completa, filtro_ano_ses, filtro_uf, filtro_escola, filtro_renda)

# Metricas vivas filtradas pelos anos selecionados (sem filtro de UF/escola/
# renda — essas dimensoes nao existem na saida consolidada de P2/P3).
metricas_vivas = metricas_vivas_completas[metricas_vivas_completas["ano"].isin(filtro_ano)]

st.title("ENEM 2022+2023 — Desigualdade Socioeconomica x Desempenho")

if base.empty and metricas_vivas.empty:
    st.warning("Nenhum registro para os filtros selecionados.")
    st.stop()

if base.empty:
    st.info(
        "Nucleo SES (KPIs, Renda, Distribuicao de notas, Mapa) sem dados para "
        "os anos selecionados — so anos vivos foram marcados. Veja Escola (P2) "
        "e Regiao (P3) abaixo, que comportam anos vivos."
    )
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Candidatos (N)", f"{len(base):,}")
    col2.metric("Media geral (CN/CH/LC/MT)", f"{base['media_geral'].mean(skipna=True):.1f}")
    col3.metric(
        "Media Redacao",
        f"{base['NU_NOTA_REDACAO'].mean(skipna=True):.1f}"
        if base["NU_NOTA_REDACAO"].notna().any()
        else "N/D",
    )
    col4.metric(
        "% Nao informado (escola)",
        f"{(base['tipo_escola'] == 'Nao informado').mean() * 100:.1f}%",
    )

aba_notas, aba_renda, aba_escola, aba_regiao, aba_mapa = st.tabs(
    ["Distribuicao de notas", "Renda x Nota (P1)", "Escola (P2)", "Regiao (P3)", "Mapa & Correlacao (US-16)"]
)

with aba_notas:
    if base.empty:
        st.info("Sem dados SES (2022/2023) para os anos selecionados.")
    else:
        nota_escolhida = st.selectbox(
            "Area", options=NOTAS, format_func=lambda c: ROTULO_NOTA[c], key="nota_dist"
        )
        valores = base[nota_escolhida].dropna()
        fig_dist = px.histogram(
            valores,
            x=nota_escolhida,
            nbins=50,
            template="plotly_dark",
            title=f"Distribuicao de {ROTULO_NOTA[nota_escolhida]} (N={len(valores):,})",
        )
        st.plotly_chart(fig_dist, use_container_width=True)

with aba_renda:
    if base.empty:
        st.info("Sem dados SES (2022/2023) para os anos selecionados.")
    else:
        tabela_renda = (
            base.groupby("faixa_renda", observed=True)["media_geral"]
            .mean()
            .reindex(ORDEM_Q006)
            .dropna()
            .reset_index()
        )
        fig_renda = px.line(
            tabela_renda,
            x="faixa_renda",
            y="media_geral",
            markers=True,
            template="plotly_dark",
            category_orders={"faixa_renda": ORDEM_Q006},
            title="Media geral por faixa de renda (ordinal)",
        )
        st.plotly_chart(fig_renda, use_container_width=True)

with aba_escola:
    tabela_escola = (
        base.groupby(["tipo_escola", "ano"], observed=True)["media_geral"]
        .mean()
        .reset_index()
    )
    tabela_escola["ano"] = tabela_escola["ano"].astype(str)
    tabela_escola_viva = tabela_p2_viva(metricas_vivas)
    tabela_escola_viva["ano"] = tabela_escola_viva["ano"].astype(str)
    tabela_escola = pd.concat([tabela_escola, tabela_escola_viva], ignore_index=True)
    if anos_vivos_disponiveis:
        st.caption(
            "Anos vivos (EP-07, US-21/US-22) via RESULTADOS — mesma definicao de "
            "media geral e gap Publica x Privada do nucleo SES, sem o eixo de renda."
        )
    fig_escola = px.bar(
        tabela_escola,
        x="ano",
        y="media_geral",
        color="tipo_escola",
        barmode="group",
        template="plotly_dark",
        category_orders={"tipo_escola": ORDEM_TP_ESCOLA},
        title="Media geral por tipo de escola e ano (gap P2)",
    )
    st.plotly_chart(fig_escola, use_container_width=True)

with aba_regiao:
    tabela_regiao_anos = (
        base.groupby(["regiao", "ano"], observed=True)["media_geral"]
        .mean()
        .reset_index()
    )
    tabela_regiao_anos["ano"] = tabela_regiao_anos["ano"].astype(str)
    tabela_regiao_viva = tabela_p3_viva(metricas_vivas)
    tabela_regiao_viva["ano"] = tabela_regiao_viva["ano"].astype(str)
    tabela_regiao = pd.concat([tabela_regiao_anos, tabela_regiao_viva], ignore_index=True)
    if anos_vivos_disponiveis:
        st.caption(
            "Anos vivos (EP-07, US-21/US-22) via RESULTADOS — mesma definicao de "
            "media geral por macrorregiao do nucleo SES, sem o eixo de renda."
        )
    fig_regiao = px.bar(
        tabela_regiao,
        x="regiao",
        y="media_geral",
        color="ano",
        barmode="group",
        template="plotly_dark",
        category_orders={"regiao": ORDEM_REGIAO},
        title="Media geral por macrorregiao e ano (P3)",
    )
    st.plotly_chart(fig_regiao, use_container_width=True)

with aba_mapa:
    if base.empty:
        st.info("Sem dados SES (2022/2023) para os anos selecionados.")
    else:
        geojson_uf = carregar_geojson_uf()

        st.subheader("Mapa coropletico por UF")
        st.caption(
            "O mapa sempre mostra as 27 UFs (ignora o filtro de UF da sidebar); a(s) "
            "UF(s) selecionada(s), se houver, ganham contorno em destaque."
        )
        tabela_uf = (
            base.groupby("SG_UF_PROVA", observed=True)["media_geral"]
            .mean()
            .reset_index()
        )
        fig_mapa = px.choropleth(
            tabela_uf,
            geojson=geojson_uf,
            locations="SG_UF_PROVA",
            featureidkey="properties.sigla",
            color="media_geral",
            color_continuous_scale="Viridis",
            template="plotly_dark",
            title="Media geral (CN/CH/LC/MT) por UF da prova",
        )
        fig_mapa.update_geos(fitbounds="locations", visible=False)
        if filtro_uf:
            fig_mapa.add_trace(
                go.Choropleth(
                    geojson=geojson_uf,
                    locations=filtro_uf,
                    z=[1] * len(filtro_uf),
                    featureidkey="properties.sigla",
                    showscale=False,
                    colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                    marker_line_color="#ff4b4b",
                    marker_line_width=3,
                )
            )
        st.plotly_chart(fig_mapa, use_container_width=True)

        st.subheader("Correlacao renda x nota (Spearman)")
        rank_renda = base["faixa_renda"].cat.codes
        mascara = (rank_renda >= 0) & base["media_geral"].notna()
        rho, p_valor = stats.spearmanr(rank_renda[mascara], base["media_geral"][mascara])
        st.metric("Spearman rho (faixa_renda x media_geral)", f"{rho:+.3f}", help=f"p={p_valor:.1e}, N={mascara.sum():,}")

        tabela_corr = (
            base.groupby("faixa_renda", observed=True)["media_geral"]
            .mean()
            .reindex(ORDEM_Q006)
            .dropna()
            .reset_index()
        )
        fig_corr = px.bar(
            tabela_corr,
            x="faixa_renda",
            y="media_geral",
            template="plotly_dark",
            category_orders={"faixa_renda": ORDEM_Q006},
            title=f"Media geral por faixa de renda (rho={rho:+.3f})",
        )
        st.plotly_chart(fig_corr, use_container_width=True)
