import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Datos de vivienda en la CDMX",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        body, .stApp {
            background-color: #261201;
        }
        h1, .stTitle {
            color: #FFD700 !important;
            text-align: center !important;
        }
        h2, h3, h4, .stHeader {
            color: #FFD700 !important;
            text-align: center !important;
        }
        p, label, span, div, .stMarkdown, .stText, .stSelectbox label {
            color: #D6D35B !important;
        }
        .stMetric {
            text-align: center !important;
        }
        .stMetric > div {
            color: #FFD700 !important;
            font-size: 28px !important;
            text-align: center !important;
        }
        .stMetric label {
            color: #FFD700 !important;
            text-align: center !important;
            font-size: 16px !important;
        }
        .metrics-center {
            display: flex;
            justify-content: center;
            text-align: center;
        }

        .stSelectbox, .stMultiSelect, .stNumberInput, .stTextInput, .stDateInput, .stRadio {
            background-color: transparent !important;
        }
        div[data-baseweb="select"],
        div[data-baseweb="input"],
        div[data-baseweb="date-picker"][class] {
            background-color: transparent !important;
            color: #D6D35B !important;
        }

        .stPlotlyChart {
            background-color: #0E1117 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Datos de vivienda en la CDMX")

st.markdown(
    """
    <p style='text-align: justify; color: #D6D35B; font-size: 16px;'>
    Este conjunto de datos ofrece un panorama de los precios de la vivienda en la Ciudad de México (CDMX), durante un periodo en el que el peso mexicano se cotizaba a aproximadamente 18.80 frente al dólar estadounidense. Proporciona una visión clara del mercado inmobiliario residencial en la CDMX, un centro urbano dinámico e influyente.
    </p>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    df = pd.read_csv('/content/housing_data_CDMX.csv', encoding='latin-1')
    return df

df = load_data()

st.header('Métricas Principales')

st.markdown("<div class='metrics-center'>", unsafe_allow_html=True)
met_col1, met_col2, met_col3 = st.columns([1,1,1])
with met_col1:
    st.metric(label='Total de registros', value=len(df))
with met_col2:
    st.metric(label='Zonas analizadas', value=df['lugar'].nunique())
with met_col3:
    st.metric(label='Tipos de propiedad', value=df['tipo_de_propiedad'].nunique())
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <p style='text-align: justify; color: #D6D35B; font-size: 16px;'>
    Incluye información clave como tipo de propiedad, ubicación, precio y superficie, lo que permite analizar cómo estas características influyen en el valor de los inmuebles dentro de una de las metrópolis más importantes de América Latina.
La base de datos proviene del trabajo original de Omar Faruk y fue posteriormente depurada y simplificada por René Cardoso, quien realizó procesos de limpieza y selección de variables para facilitar un análisis más claro, eficiente y orientado a las características más relevantes del mercado.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

bins_mxn = [0, 1_000_000, 3_000_000, 7_000_000, 15_000_000, 35_000_000, df['precio_aprox_local'].max()]
bins_usd = [0, 54_000, 162_000, 378_000, 810_000, 1_890_000, df['precio_aprox_usd'].max()]

labels_mxn = [
    "Económica (< $1M MXN)",
    "Media-baja ($1M – $3M MXN)",
    "Media ($3M – $7M MXN)",
    "Media-alta ($7M – $15M MXN)",
    "Alta ($15M – $35M MXN)",
    "Lujo (> $35M MXN)"
]

labels_usd = [
    "Económica (< $54K USD)",
    "Media-baja ($54K – $162K USD)",
    "Media ($162K – $378K USD)",
    "Media-alta ($378K – $810K USD)",
    "Alta ($810K – $1.89M USD)",
    "Lujo (> $1.89M USD)"
]

df['rango_precio_mxn'] = pd.cut(df['precio_aprox_local'], bins=bins_mxn, labels=labels_mxn, include_lowest=True)
df['rango_precio_usd'] = pd.cut(df['precio_aprox_usd'], bins=bins_usd, labels=labels_usd, include_lowest=True)

labels_mxn = ["Todos"] + labels_mxn
labels_usd = ["Todos"] + labels_usd

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
    </style>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Frecuencia por lugar",
    "Distribución por tipo y lugar",
    "Mapa de calor de precios",
    "Visualización Geográfica"
])

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
        property_counts = df_filtered.groupby(['lugar', 'tipo_de_propiedad']).size().reset_index(name='frecuencia')

        fig1 = px.bar(
            property_counts,
            x='lugar',
            y='frecuencia',
            color='tipo_de_propiedad',
            color_discrete_sequence=px.colors.qualitative.D3,
            orientation='v',
            title=f'Frecuencia de tipo de propiedad por lugar ({rango})'
        )

        fig1.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            xaxis_title='Lugar',
            yaxis_title='Frecuencia',
            font_color='#D6D35B'
        )

        st.plotly_chart(fig1, use_container_width=True)

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

        fig2.update_layout(
            paper_bgcolor='#0E1117',
            plot_bgcolor='#0E1117'
        )

        st.plotly_chart(fig2, use_container_width=True)

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

    fig3.update_layout(
        paper_bgcolor='#0E1117',
        plot_bgcolor='#0E1117',
        font_color='#D6D35B'
    )

    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Visualización Geográfica")