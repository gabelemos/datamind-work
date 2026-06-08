import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Tendências", page_icon="📈", layout="wide")
st.title("📈 Tendências")
st.caption("Os anos 2026 e 2027 são projeções baseadas em regressão linear — não consideram fatores externos.")
st.divider()

df   = st.session_state.df
kpis = st.session_state.kpis


def _prever(anos: np.ndarray, counts: np.ndarray, anos_alvo: list) -> list:
    """Retorna previsões para anos_alvo usando regressão linear."""
    coef = np.polyfit(anos.astype(float), counts.astype(float), 1)
    return [max(0, np.poly1d(coef)(a)) for a in anos_alvo]


ANOS_PREV = [2026, 2027]

# ── TENDÊNCIA ANUAL ───────────────────────────────────────────────────────────
st.subheader("Evolução Anual de Notificações")
trend_anual = kpis["trends"]["trend_anual"].copy()

if not trend_anual.empty:
    trend_anual["ano"] = pd.to_datetime(trend_anual["DT_NOTIFIC"]).dt.year
    anos   = trend_anual["ano"].values
    counts = trend_anual["count"].values
    prev   = _prever(anos, counts, ANOS_PREV)

    # ponto de conexão: último ano histórico + projeção
    x_prev = [anos[-1]] + ANOS_PREV
    y_prev = [counts[-1]] + prev

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos, y=counts,
        mode="lines+markers", name="Histórico",
        line=dict(color="#1a5276", width=2.5), marker=dict(size=8),
    ))
    fig.add_trace(go.Scatter(
        x=x_prev, y=y_prev,
        mode="lines+markers", name="Projeção",
        line=dict(color="#e74c3c", width=2, dash="dash"),
        marker=dict(size=9, symbol="diamond"),
        text=[""] + [f"~{int(v):,}".replace(",", ".") for v in prev],
        textposition="top center",
    ))
    fig.add_vline(x=anos[-1] + 0.5, line_dash="dot", line_color="#aaa",
        annotation_text="Projeção →", annotation_position="top left")
    fig.add_vline(x=2020, line_dash="dash", line_color="#e74c3c",
        annotation_text="Início COVID-19", annotation_position="top right")
    fig.update_layout(
        plot_bgcolor="white",
        xaxis=dict(title="Ano", tickmode="linear", dtick=1),
        yaxis_title="Notificações",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── TENDÊNCIA POR SEXO ────────────────────────────────────────────────────────
st.subheader("Tendência por Sexo")
trend_sexo = kpis["trends"]["trend_por_sexo"].copy()

if not trend_sexo.empty:
    id_col    = "DT_NOTIFIC"
    sexo_cols = [c for c in trend_sexo.columns if c != id_col]
    trend_sexo["ano"] = pd.to_datetime(trend_sexo[id_col]).dt.year
    anos = trend_sexo["ano"].values

    _SEXO_LABEL = {"M": "Masculino", "F": "Feminino", "I": "Não informado"}
    cores = ["#1a5276", "#2e86c1", "#aed6f1"]

    fig2 = go.Figure()
    for i, col in enumerate(sexo_cols):
        counts = trend_sexo[col].values
        prev   = _prever(anos, counts, ANOS_PREV)
        cor    = cores[i % len(cores)]
        label  = _SEXO_LABEL.get(col, col)

        fig2.add_trace(go.Scatter(
            x=anos, y=counts,
            mode="lines+markers", name=label,
            line=dict(color=cor, width=2), marker=dict(size=7),
        ))
        fig2.add_trace(go.Scatter(
            x=[anos[-1]] + ANOS_PREV, y=[counts[-1]] + prev,
            mode="lines+markers", name=f"{label} (proj.)",
            line=dict(color=cor, width=2, dash="dash"),
            marker=dict(size=8, symbol="diamond"),
            showlegend=True,
        ))

    fig2.add_vline(x=anos[-1] + 0.5, line_dash="dot", line_color="#aaa",
        annotation_text="Projeção →", annotation_position="top left")
    fig2.update_layout(
        plot_bgcolor="white",
        xaxis=dict(title="Ano", tickmode="linear", dtick=1),
        yaxis_title="Notificações",
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── TENDÊNCIA MENSAL ──────────────────────────────────────────────────────────
st.subheader("Tendência Mensal")
trend_mensal = kpis["trends"]["trend_mensal"].copy()

if not trend_mensal.empty:
    counts = trend_mensal["count"].values
    meses  = np.arange(len(counts), dtype=float)
    prev   = _prever(meses, counts, [len(counts), len(counts) + 11])

    # gera datas mensais para 2026 e 2027
    ultima_data  = pd.to_datetime(trend_mensal["DT_NOTIFIC"].iloc[-1])
    datas_futuro = pd.date_range(start=ultima_data + pd.DateOffset(months=1), periods=24, freq="MS")
    vals_futuro  = _prever(meses, counts, np.arange(len(counts), len(counts) + 24, dtype=float))

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=trend_mensal["DT_NOTIFIC"], y=counts,
        mode="lines", name="Histórico",
        fill="tozeroy", fillcolor="rgba(46,134,193,0.2)",
        line=dict(color="#2e86c1", width=2),
    ))
    fig3.add_trace(go.Scatter(
        x=[trend_mensal["DT_NOTIFIC"].iloc[-1]] + list(datas_futuro),
        y=[counts[-1]] + vals_futuro,
        mode="lines", name="Projeção",
        fill="tozeroy", fillcolor="rgba(231,76,60,0.1)",
        line=dict(color="#e74c3c", width=1.5, dash="dash"),
    ))
    fig3.add_vline(x=str(ultima_data + pd.DateOffset(months=1))[:10],
        line_dash="dot", line_color="#aaa",
        annotation_text="Projeção →", annotation_position="top left")
    fig3.update_layout(
        plot_bgcolor="white",
        xaxis_title="Mês", yaxis_title="Notificações",
    )
    st.plotly_chart(fig3, use_container_width=True)
