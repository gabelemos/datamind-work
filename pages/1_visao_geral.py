import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Visão Geral", page_icon="📊", layout="wide")
st.title("📊 Visão Geral")
st.divider()

df   = st.session_state.df
kpis = st.session_state.kpis

# ── KPIs ──────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
k = kpis.get("kpis", {})
col1.metric("Total de Notificações", f"{k.get('total_registros', 0):,}".replace(",", "."))
col2.metric("Média de Idade",        f"{k.get('media_idade', 0):.1f} anos")
col3.metric("Mediana de Idade",      f"{k.get('mediana_idade', 0):.1f} anos")
col4.metric("Anos na Base",          str(k.get("anos_disponiveis", [])))

st.divider()

# ── CASOS POR ANO ─────────────────────────────────────────────────────────────
st.subheader("Notificações por Ano")
casos_ano = kpis["aggregations"]["casos_por_ano"].copy()
casos_ano["ANO"] = casos_ano["ANO"].astype(str)

fig = px.bar(casos_ano, x="ANO", y="count",
    color="count", color_continuous_scale="Blues",
    labels={"ANO": "Ano", "count": "Notificações"},
    text="count")
fig.update_traces(textposition="outside")
fig.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── DISTRIBUIÇÕES ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Por Sexo")
    casos_sexo = kpis["aggregations"]["casos_por_sexo"]
    fig2 = px.pie(casos_sexo, names="CS_SEXO", values="count",
        color_discrete_sequence=px.colors.sequential.Blues_r)
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Por Faixa Etária")
    faixas = kpis["aggregations"]["casos_por_faixa_idade"]
    fig3 = px.bar(faixas, x="age_range", y="count",
        color="count", color_continuous_scale="Blues",
        labels={"age_range": "Faixa Etária", "count": "Notificações"})
    fig3.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("Por Raça/Cor")
    casos_raca = kpis["aggregations"]["casos_por_raca"]
    fig4 = px.bar(casos_raca, x="count", y="CS_RACA", orientation="h",
        color="count", color_continuous_scale="Blues",
        labels={"CS_RACA": "Raça/Cor", "count": "Notificações"})
    fig4.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("Por Evolução do Caso")
    casos_evolucao = kpis["aggregations"]["casos_por_evolucao"]
    fig5 = px.pie(casos_evolucao, names="EVOLUCAO", values="count",
        color_discrete_sequence=px.colors.sequential.Blues_r)
    fig5.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig5, use_container_width=True)
