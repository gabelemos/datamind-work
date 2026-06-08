import streamlit as st

# configuração da página principal
st.set_page_config(
    page_title="DataMind — Work",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# estilo global
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { font-size: 15px; }
        .block-container { padding-top: 2rem; }
        h1, h2, h3 { color: #1a5276; }
        .stMetric label { font-size: 13px; color: #555; }
    </style>
""", unsafe_allow_html=True)

# carrega o dataset uma vez e guarda no session_state
if "df" not in st.session_state:
    with st.spinner("Carregando dados do DataSUS..."):
        from converter import get_dataset
        st.session_state.df = get_dataset()

if "kpis" not in st.session_state:
    from analytics import build_kpis
    st.session_state.kpis = build_kpis(st.session_state.df)

# página inicial
st.title("🧠 DataMind — Work")
st.markdown("**Dashboard de Saúde Mental no Trabalho** | Dados: SINAN/DataSUS — Base MENTBR")
st.divider()

col1, col2, col3, col4 = st.columns(4)

kpis = st.session_state.kpis.get("kpis", {})

col1.metric("Total de Notificações", f"{kpis.get('total_registros', 0):,}".replace(",", "."))
col2.metric("Anos Disponíveis", len(kpis.get("anos_disponiveis", [])))
col3.metric("Média de Idade", f"{kpis.get('media_idade', 0):.1f} anos")
col4.metric("Estado com mais casos", kpis.get("top_estado", {}).get("SG_UF_NOT", "-"))

st.divider()
st.markdown("#### Navegue pelas páginas no menu lateral ←")
st.markdown("""
| Página | Descrição |
|---|---|
| 📊 Visão Geral | KPIs e distribuições gerais |
| ⚖️ Comparações | Pré vs pós pandemia |
| 📈 Tendências | Evolução ano a ano |
| 🗺️ Mapa | Distribuição geográfica |
| 🔬 Análises Estatísticas | Estatísticas descritivas |
""")

st.divider()
st.caption("Dados públicos disponíveis em [datasus.saude.gov.br](https://datasus.saude.gov.br) | Base MENTBR 2017–2025")
