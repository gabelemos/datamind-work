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
_sexo_raw = k.get("top_sexo", {}).get("CS_SEXO", "-")
_sexo_label = {"M": "Masculino", "F": "Feminino", "I": "Não informado"}.get(_sexo_raw, _sexo_raw)
col3.metric("Sexo Predominante", _sexo_label)
anos = k.get("anos_disponiveis", [])
anos_label = f"{min(anos)}–{max(anos)} ({len(anos)} anos)" if anos else "-"
col4.metric("Anos na Base", anos_label)

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
    casos_sexo = kpis["aggregations"]["casos_por_sexo"].copy()
    casos_sexo["CS_SEXO"] = casos_sexo["CS_SEXO"].map(
        {"M": "Masculino", "F": "Feminino", "I": "Não informado"}
    ).fillna(casos_sexo["CS_SEXO"])
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
    casos_raca = kpis["aggregations"]["casos_por_raca"].copy()
    casos_raca["CS_RACA"] = casos_raca["CS_RACA"].astype(str).map({
        "1": "Branca", "2": "Preta", "3": "Amarela",
        "4": "Parda", "5": "Indígena", "9": "Ignorado", "": "Não informado",
    }).fillna(casos_raca["CS_RACA"].astype(str))
    fig4 = px.bar(casos_raca, x="count", y="CS_RACA", orientation="h",
        color="count", color_continuous_scale="Blues",
        labels={"CS_RACA": "Raça/Cor", "count": "Notificações"})
    fig4.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("Por Evolução do Caso")
    casos_evolucao = kpis["aggregations"]["casos_por_evolucao"].copy()
    casos_evolucao["EVOLUCAO"] = casos_evolucao["EVOLUCAO"].astype(str).map({
        "1": "Cura",
        "2": "Óbito pelo agravo",
        "3": "Óbito por outras causas",
        "4": "Óbito em investigação",
        "5": "Transferência",
        "6": "Alta com sequela",
        "7": "Alta por abandono",
        "8": "Encerrado por outra causa",
        "9": "Ignorado",
        "":  "Não informado",
    }).fillna(casos_evolucao["EVOLUCAO"].astype(str))
    fig5 = px.pie(casos_evolucao, names="EVOLUCAO", values="count",
        color_discrete_sequence=px.colors.sequential.Blues_r)
    fig5.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig5, use_container_width=True)
