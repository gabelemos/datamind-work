import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Tendências", page_icon="📈", layout="wide")
st.title("📈 Tendências")
st.divider()

df   = st.session_state.df
kpis = st.session_state.kpis

# ── TENDÊNCIA ANUAL ───────────────────────────────────────────────────────────
st.subheader("Evolução Anual de Notificações")
trend_anual = kpis["trends"]["trend_anual"]

if not trend_anual.empty:
    fig = px.line(trend_anual, x="DT_NOTIFIC", y="count",
        markers=True, color_discrete_sequence=["#1a5276"],
        labels={"DT_NOTIFIC": "Ano", "count": "Notificações"})
    fig.update_traces(line_width=2.5, marker_size=8)
    fig.update_layout(plot_bgcolor="white")

    # linha divisória pandemia
    fig.add_vline(x="2020-01-01", line_dash="dash", line_color="#e74c3c",
        annotation_text="Início COVID-19", annotation_position="top right")

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── TENDÊNCIA POR SEXO ────────────────────────────────────────────────────────
st.subheader("Tendência por Sexo")
trend_sexo = kpis["trends"]["trend_por_sexo"]

if not trend_sexo.empty:
    # transforma de wide para long
    id_col = "DT_NOTIFIC"
    value_cols = [c for c in trend_sexo.columns if c != id_col]
    melted = trend_sexo.melt(id_vars=id_col, value_vars=value_cols,
        var_name="Sexo", value_name="count")

    fig2 = px.line(melted, x=id_col, y="count", color="Sexo",
        markers=True, color_discrete_sequence=["#1a5276", "#2e86c1", "#aed6f1"],
        labels={id_col: "Ano", "count": "Notificações"})
    fig2.update_traces(line_width=2)
    fig2.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── TENDÊNCIA MENSAL ──────────────────────────────────────────────────────────
st.subheader("Tendência Mensal")
trend_mensal = kpis["trends"]["trend_mensal"]

if not trend_mensal.empty:
    fig3 = px.area(trend_mensal, x="DT_NOTIFIC", y="count",
        color_discrete_sequence=["#2e86c1"],
        labels={"DT_NOTIFIC": "Mês", "count": "Notificações"})
    fig3.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig3, use_container_width=True)
