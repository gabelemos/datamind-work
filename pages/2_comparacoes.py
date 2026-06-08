import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Comparações", page_icon="⚖️", layout="wide")
st.title("⚖️ Comparações — Pré vs Pós Pandemia")
st.markdown("Comparando **2017–2019** (pré) com **2022–2025** (pós pandemia)")
st.divider()

df   = st.session_state.df
kpis = st.session_state.kpis

# ── COMPARAÇÃO GERAL ──────────────────────────────────────────────────────────
comp = kpis["comparisons"]["before_after_pandemic"]
if not comp.empty:
    row = comp.iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Pré-pandemia (2017–2019)", f"{int(row.get('count_2017-2019', 0)):,}".replace(",", "."))
    col2.metric("Pós-pandemia (2022–2025)", f"{int(row.get('count_2020-2024', 0)):,}".replace(",", "."))
    pct = row.get("pct_change", 0)
    col3.metric("Variação %", f"{pct:.1f}%", delta=f"{pct:.1f}%")

st.divider()

# ── COMPARAÇÃO POR ESTADO ─────────────────────────────────────────────────────
st.subheader("Variação por Estado")
estado_comp = kpis["comparisons"]["estado_before_after"]
if not estado_comp.empty:
    # pega colunas dinamicamente
    count_cols = [c for c in estado_comp.columns if c.startswith("count_")]
    if len(count_cols) == 2:
        col_pre, col_pos = count_cols[0], count_cols[1]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Pré-pandemia", x=estado_comp["SG_UF_NOT"], y=estado_comp[col_pre], marker_color="#aed6f1"))
        fig.add_trace(go.Bar(name="Pós-pandemia", x=estado_comp["SG_UF_NOT"], y=estado_comp[col_pos], marker_color="#1a5276"))
        fig.update_layout(barmode="group", plot_bgcolor="white",
            xaxis_title="Estado", yaxis_title="Notificações")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── COMPARAÇÃO POR SEXO ───────────────────────────────────────────────────────
st.subheader("Variação por Sexo")
sexo_comp = kpis["comparisons"]["sexo_before_after"]
if not sexo_comp.empty:
    count_cols = [c for c in sexo_comp.columns if c.startswith("count_")]
    if len(count_cols) == 2:
        col_pre, col_pos = count_cols[0], count_cols[1]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Pré-pandemia", x=sexo_comp["CS_SEXO"], y=sexo_comp[col_pre], marker_color="#aed6f1"))
        fig2.add_trace(go.Bar(name="Pós-pandemia", x=sexo_comp["CS_SEXO"], y=sexo_comp[col_pos], marker_color="#1a5276"))
        fig2.update_layout(barmode="group", plot_bgcolor="white",
            xaxis_title="Sexo", yaxis_title="Notificações")
        st.plotly_chart(fig2, use_container_width=True)
