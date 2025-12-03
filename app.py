import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
from datetime import datetime
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(
    page_title="Datos de vivienda en la CDMX",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    /* Fondo general de la página */
    .main {
        background-color: #231709;
    }

    /* Color de los títulos y texto */
    h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {
        color: #d0bd19 !important;
    }

    /* Header superior con mismo color que el fondo */
    header.css-18ni7ap {
        background-color: #231709 !important;
        color: #d0bd19 !important;
    }
    header.css-1avcm0n {
        background-color: #231709 !important;
        color: #d0bd19 !important;
    }

    /* Métricas principales */
    div[data-testid="metric-value"] {
        color: #d1bd19 !important;
        font-weight: bold !important;
    }
    div[data-testid="metric-label"] {
        color: #d0bd19 !important;
    }

</style>
""", unsafe_allow_html=True)

# Banner superior
st.image("banner.png", use_container_width=True)

# Título principal
st.title("Datos de vivienda en la CDMX")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv('/content/housing_data_CDMX.csv', encoding='latin-1')
    return df

df = load_data()

# Métricas principales
st.header('Métricas Principales')
met_col1, met_col2, met_col3 = st.columns(3)

with met_col1:
    st.metric(label='Total de registros', value=len(df))
with met_col2:
    st.metric(label='Zonas analizadas', value=df['lugar'].nunique())
with met_col3:
    st.metric(label='Tipos de propiedad', value=df['tipo_de_propiedad'].nunique())

st.markdown("---")

# Rango de precios
bins_mxn = [0, 1_000_000, 3_000_000, 7_000_000, 15_000_000, 35_000_000, df['precio_aprox_local'].max()]
bins_usd = [0, 54_000, 162_000, 378_000, 810_000, 1_890_000, df['precio_aprox_usd'].max()]

labels_mxn = [
    "Económica (< $1M MXN)", "Media-baja ($1M – $3M MXN)", "Media ($3M – $7M MXN)",
    "Media-alta ($7M – $15M MXN)", "Alta ($15M – $35M MXN)", "Lujo (> $35M MXN)"
]

labels_usd = [
    "Económica (< $54K USD)", "Media-baja ($54K – $162K USD)", "Media ($162K – $378K USD)",
    "Media-alta ($378K – $810K USD)", "Alta ($810K – $1.89M USD)", "Lujo (> $1.89M USD)"
]

df['rango_precio_mxn'] = pd.cut(df['precio_aprox_local'], bins=bins_mxn, labels=labels_mxn, include_lowest=True)
df['rango_precio_usd'] = pd.cut(df['precio_aprox_usd'], bins=bins_usd, labels=labels_usd, include_lowest=True)

labels_mxn = ["Todos"] + labels_mxn
labels_usd = ["Todos"] + labels_usd

# Estilo tabs
st.markdown("""
<style>
div[data-baseweb="tab-list"] {
    display: flex;
    justify-content: space-between;
    width: 100%;
}
div[data-baseweb="tab"] {
    flex-grow: 1;
    text-align: center !important;
}
div[data-baseweb="tab"]:hover {
    background-color: #d1bd19 !important;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Frecuencia por lugar",
    "Distribución por tipo y lugar",
    "Mapa de calor de precios",
    "Visualización Geográfica"
])

# TAB 1
with tab1:
    st.subheader('Frecuencia de tipo de propiedad por lugar')
    moneda = st.selectbox("Selecciona la moneda:", ["MXN", "USD"], key="moneda_tab1")

    if moneda == "MXN":
        rango = st.selectbox("Selecciona el rango de precio:", labels_mxn, key="rango_mxn_tab1")
        df_filtered = df if rango == "Todos" else df[df['rango_precio_mxn'] == rango]
    else:
        rango = st.selectbox("Selecciona el rango de precio:", labels_usd, key="rango_usd_tab1")
        df_filtered = df if rango == "Todos" else df[df['rango_precio_usd'] == rango]

    if df_filtered.empty:
        st.warning("No hay propiedades en este rango de precio.")
    else:
        property_counts = (
            df_filtered.groupby(['lugar', 'tipo_de_propiedad'])
            .size()
            .reset_index(name='frecuencia')
        )

        fig1 = px.bar(
            property_counts,
            x='lugar',
            y='frecuencia',
            color='tipo_de_propiedad',
            color_discrete_sequence=px.colors.qualitative.D3,
            title=f'Frecuencia de tipo de propiedad por lugar ({rango})'
        )

        fig1.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor='white',
            xaxis_title='Lugar',
            yaxis_title='Frecuencia'
        )

        st.plotly_chart(fig1, use_container_width=True)

# TAB 2
with tab2:
    st.subheader('Distribución de tipos de propiedad por lugar')
    moneda = st.selectbox("Selecciona la moneda:", ["MXN", "USD"], key="moneda_tab2")

    if moneda == "MXN":
        rango = st.selectbox("Selecciona el rango de precio:", labels_mxn, key="rango_mxn_tab2")
        df_filtered = df if rango == "Todos" else df[df['rango_precio_mxn'] == rango]
    else:
        rango = st.selectbox("Selecciona el rango de precio:", labels_usd, key="rango_usd_tab2")
        df_filtered = df if rango == "Todos" else df[df['rango_precio_usd'] == rango]

    if df_filtered.empty:
        st.warning("No hay propiedades en este rango de precio.")
    else:
        property_counts = (
            df_filtered.groupby(['lugar', 'tipo_de_propiedad'])
            .size()
            .reset_index(name='frecuencia')
        )

        fig2 = px.sunburst(
            property_counts,
            path=['tipo_de_propiedad', 'lugar'],
            values='frecuencia',
            color='frecuencia',
            color_continuous_scale='Viridis',
            title=f'Distribución jerárquica de propiedades ({rango})'
        )

        st.plotly_chart(fig2, use_container_width=True)

# TAB 3
with tab3:
    st.subheader('Mapa de calor del precio promedio por tipo de propiedad y lugar')

    average_price = (
        df.groupby(['tipo_de_propiedad', 'lugar'])['precio_aprox_local']
        .mean()
        .reset_index()
    )

    fig3 = px.density_heatmap(
        average_price,
        x='lugar',
        y='tipo_de_propiedad',
        z='precio_aprox_local',
        color_continuous_scale='RdYlGn',
    )

    st.plotly_chart(fig3, use_container_width=True)

# TAB 4
with tab4:
    st.subheader('Mapa geográfico de propiedades')
    fig4 = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="lugar",
        hover_name="lugar",
        hover_data=["tipo_de_propiedad", "precio_aprox_local"],
        zoom=10,
        height=600
    )
    fig4.update_layout(mapbox_style="open-street-map")
    fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig4, use_container_width=True)
