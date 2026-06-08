import streamlit as st
import plotly.express as px
import pandas as pd
import requests

st.set_page_config(page_title="Mapa", page_icon="🗺️", layout="wide")
st.title("🗺️ Mapa — Distribuição Geográfica")
st.divider()

df   = st.session_state.df
kpis = st.session_state.kpis

# mapa de código numérico para sigla
UF_PARA_SIGLA = {
    "11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO",
    "21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL",
    "28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR",
    "42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF",
}
SIGLA_PARA_NOME = {
    "RO":"Rondônia","AC":"Acre","AM":"Amazonas","RR":"Roraima","PA":"Pará",
    "AP":"Amapá","TO":"Tocantins","MA":"Maranhão","PI":"Piauí","CE":"Ceará",
    "RN":"Rio Grande do Norte","PB":"Paraíba","PE":"Pernambuco","AL":"Alagoas",
    "SE":"Sergipe","BA":"Bahia","MG":"Minas Gerais","ES":"Espírito Santo",
    "RJ":"Rio de Janeiro","SP":"São Paulo","PR":"Paraná","SC":"Santa Catarina",
    "RS":"Rio Grande do Sul","MS":"Mato Grosso do Sul","MT":"Mato Grosso",
    "GO":"Goiás","DF":"Distrito Federal",
}

# carrega GeoJSON do Brasil
@st.cache_data
def carregar_geojson():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    return requests.get(url).json()

geojson = carregar_geojson()

# prepara dados por UF
casos_uf = kpis["aggregations"]["casos_por_estado"].copy()
casos_uf["UF"] = casos_uf["SG_UF_NOT"].astype(str).str.strip().map(UF_PARA_SIGLA).fillna(casos_uf["SG_UF_NOT"].astype(str).str.strip())
casos_uf["Estado"] = casos_uf["UF"].map(SIGLA_PARA_NOME).fillna(casos_uf["UF"])

# extrai a propriedade correta do GeoJSON pra fazer o match
# o GeoJSON usa "sigla" como chave
fig = px.choropleth(
    casos_uf,
    geojson=geojson,
    locations="UF",
    featureidkey="properties.sigla",
    color="count",
    hover_name="Estado",
    hover_data={"count": True, "UF": False},
    color_continuous_scale="Blues",
    labels={"count": "Notificações"},
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=550)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── RANKING DE ESTADOS ────────────────────────────────────────────────────────
st.subheader("Ranking de Estados")
col1, col2 = st.columns([2, 1])

with col1:
    fig2 = px.bar(casos_uf.head(15).sort_values("count"),
        x="count", y="Estado", orientation="h",
        color="count", color_continuous_scale="Blues",
        labels={"count": "Notificações", "Estado": ""})
    fig2.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.dataframe(
        casos_uf[["Estado", "count"]].rename(columns={"count": "Notificações"}).reset_index(drop=True),
        use_container_width=True, hide_index=True
    )
