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

_UF_SIGLA = {
    "11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO",
    "21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL",
    "28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR",
    "42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF",
}
_top_uf_raw = str(kpis.get("top_estado", {}).get("SG_UF_NOT", "-"))
_top_uf = _UF_SIGLA.get(_top_uf_raw, _top_uf_raw)

col1.metric("Total de Notificações", f"{kpis.get('total_registros', 0):,}".replace(",", "."))
_anos = kpis.get("anos_disponiveis", [])
_anos_label = f"{min(_anos)}–{max(_anos)}" if _anos else "-"
col2.metric("Anos Disponíveis", _anos_label)
col3.metric("Média de Idade", f"{kpis.get('media_idade', 0):.1f} anos")
col4.metric("Estado com mais casos", _top_uf)

st.divider()
st.markdown("<h2 style='text-align: center;'>Navegue pelas páginas no menu lateral ←</h2>", unsafe_allow_html=True)
st.markdown("""
<div style='display: flex; justify-content: center;'>

| Página | Descrição |
|---|---|
| 📊 Visão Geral | KPIs e distribuições gerais |
| ⚖️ Comparações | Pré vs pós pandemia |
| 📈 Tendências | Evolução ano a ano |
| 🗺️ Mapa | Distribuição geográfica |
| 🔬 Análises Estatísticas | Estatísticas descritivas |

</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Dados públicos disponíveis em [datasus.saude.gov.br](https://datasus.saude.gov.br) | Base MENTBR 2017–2025")
