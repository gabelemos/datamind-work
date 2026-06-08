import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(page_title="Análises Estatísticas", page_icon="🔬", layout="wide")
st.title("🔬 Análises Estatísticas")
st.divider()

df   = st.session_state.df
kpis = st.session_state.kpis

# ── ESTATÍSTICAS DESCRITIVAS ──────────────────────────────────────────────────
st.subheader("Estatísticas Descritivas — Idade")

idade = pd.to_numeric(df["NU_IDADE_N"], errors="coerce").dropna()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Média",    f"{idade.mean():.1f}")
col2.metric("Mediana",  f"{idade.median():.1f}")
col3.metric("Desvio Padrão", f"{idade.std():.1f}")
col4.metric("Mínimo",   f"{idade.min():.0f}")
col5.metric("Máximo",   f"{idade.max():.0f}")

st.divider()

# ── HISTOGRAMA DE IDADE ───────────────────────────────────────────────────────
st.subheader("Distribuição de Idade")
fig = px.histogram(df, x=pd.to_numeric(df["NU_IDADE_N"], errors="coerce"),
    nbins=30, color_discrete_sequence=["#1a5276"],
    labels={"x": "Idade", "count": "Frequência"})
fig.update_layout(plot_bgcolor="white", bargap=0.05)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── ESCOLARIDADE ──────────────────────────────────────────────────────────────
st.subheader("Distribuição por Escolaridade")
_ESCOL_MAP = {
    "00": "Analfabeto",
    "01": "Fund. I incompleto",
    "02": "Fund. I completo",
    "03": "Fund. II incompleto",
    "04": "Fund. II completo",
    "05": "Médio incompleto",
    "06": "Médio completo",
    "07": "Superior incompleto",
    "08": "Superior completo",
    "09": "Ignorado",
    "10": "Não se aplica",
    "":  "Não informado",
}
_ESCOL_ORDEM = list(_ESCOL_MAP.values())

casos_escol = kpis["aggregations"]["casos_por_escolaridade"].copy()
casos_escol["CS_ESCOL_N"] = casos_escol["CS_ESCOL_N"].astype(str).map(_ESCOL_MAP).fillna(casos_escol["CS_ESCOL_N"].astype(str))
casos_escol["_ordem"] = casos_escol["CS_ESCOL_N"].map({v: i for i, v in enumerate(_ESCOL_ORDEM)}).fillna(99)
casos_escol = casos_escol.sort_values("_ordem")

fig2 = px.bar(casos_escol, x="CS_ESCOL_N", y="count",
    color="count", color_continuous_scale="Blues",
    labels={"CS_ESCOL_N": "Escolaridade", "count": "Notificações"},
    text="count")
fig2.update_traces(textposition="outside")
fig2.update_layout(
    coloraxis_showscale=False, plot_bgcolor="white",
    xaxis_tickangle=-30,
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── TABELA COMPLETA ───────────────────────────────────────────────────────────
st.subheader("Dados Brutos")
colunas_exibir = [c for c in ["ANO", "SG_UF_NOT", "CS_SEXO", "NU_IDADE_N", "CS_RACA", "CS_ESCOL_N", "EVOLUCAO"] if c in df.columns]

with st.expander("Ver tabela completa"):
    st.dataframe(df[colunas_exibir].head(500), use_container_width=True, hide_index=True)
