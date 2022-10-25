import pydeck as pdk
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
  page_icon=":thumbs_up:",
  layout="wide",
  
)

@st.cache
def carga_data():
  return pd.read_excel("carga-bip.xlsx", header=9)

# Se lee la información de forma óptima
bip = carga_data()

st.header("Challenge de Visualizaciones")
st.info("##### Top 5 de Puntos de Carga por Comuna")

################################################################################################
col_bar, col_pie, col_table = st.columns(3, gap="large")
# Agrupar los datos, en base a la columna donde están las comunas
# Se genera la serie de la agrupación usando "size()"
group_comuna = bip.groupby(["MAIPU"]).size()
# Se ordenan de mayor a menor, gracias al uso del parámetros "ascending=False"
group_comuna.sort_values(axis="index", ascending=False, inplace=True)
# Ya se pueden obtener los 5 primeros registros
top5 = group_comuna[0:5]

def formato_porciento(dato: float):
  return f"{round(dato, ndigits=2)}%"


with col_bar:
  bar = plt.figure()
  top5.plot.bar(
    title="Cantidad de Puntos de Carga por Comuna",
    label="Total de Puntos",
    xlabel="Comunas",
    ylabel="Puntos de Carga",
    color="lightblue",
    grid=True,
  ).plot()
  st.pyplot(bar)

with col_pie:
  pie = plt.figure()
  top5.plot.pie(
    y="index",
    title="Cantidad de Puntos de Carga por Comuna",
    legend=None,
    autopct=formato_porciento
  ).plot()
  st.pyplot(pie)

with col_table:
  pie = plt.figure()
  top5.plot.line(
    title="Cantidad de Puntos de Carga por Comuna",
    label="Total de Puntos",
    xlabel="Comunas",
    ylabel="Puntos de Carga",
    color="lightblue",
    grid=True
  ).plot()
  st.pyplot(pie)

################################################################################################
st.info("##### Agrupación Puntos de Carga por Comuna")

col_sel, col_map = st.columns([1,2])

# Crear grupos por cantidad de puntos
group_20 = group_comuna.apply(lambda x: x if x <= 20 else None).dropna(axis=0)
group_60 = group_comuna.apply(lambda x: x if x > 20 and x <= 60 else None).dropna(axis=0)
group_max = group_comuna.apply(lambda x: x if x > 60 else None).dropna(axis=0)


with col_sel:
  comunas_agrupadas = st.multiselect(
    label="Filtrar por grupos de Comuna", 
    options=["Menos de 20 Puntos", "21 a 60 Puntos", "Más de 60 Puntos"],
    help="Selecciona la agrupación a mostrar",
    default=[]
  )

filtrar = []

if "Menos de 20 Puntos" in comunas_agrupadas:
  filtrar = filtrar + group_20.index.tolist()

if "21 a 60 Puntos" in comunas_agrupadas:
  filtrar = filtrar + group_60.index.tolist()

if "Más de 60 Puntos" in comunas_agrupadas:
  filtrar = filtrar + group_max.index.tolist()

# Obtener parte de la información
geo_puntos_comuna = bip[ ["CODIGO","NOMBRE FANTASIA", "CERRO BLANCO 625", "MAIPU", "LATITUD", "LONGITUD"]].rename(columns={
  "NOMBRE FANTASIA": "Negocio", 
  "CERRO BLANCO 625": "Dirección", 
  "MAIPU": "Comuna",
})
geo_puntos_comuna.dropna(subset=["Comuna"], inplace=True)
geo_data = geo_puntos_comuna

# Aplicar filtro de Comuna
if filtrar:
  geo_data = geo_puntos_comuna.query("Comuna == @filtrar")

# Obtener el punto promedio entre todas las georeferencias
avg_lat = np.median(geo_data["LATITUD"])
avg_lng = np.median(geo_data["LONGITUD"])

puntos_mapa = pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=avg_lat,
        longitude=avg_lng,
        zoom=10,
        min_zoom=10,
        max_zoom=15,
        pitch=20,
    ),
    layers=[
      pdk.Layer(
        "ScatterplotLayer",
        data=geo_data,
        pickable=True,
        auto_highlight=True,
        get_position='[LONGITUD, LATITUD]',
        filled=True,
        opacity=1,
        radius_scale=10,
        radius_min_pixels=2,
        # radius_max_pixels=10,
        # line_width_min_pixels=0.01,
      )      
    ],
    tooltip={
      "html": "<b>Negocio: </b> {Negocio} <br /> "
              "<b>Dirección: </b> {Dirección} <br /> "
              "<b>Comuna: </b> {Comuna} <br /> "
              "<b>Código: </b> {CODIGO} <br /> "
              "<b>Georeferencia (Lat, Lng): </b>[{LATITUD}, {LONGITUD}] <br /> "
    }
)

with col_map:
  st.write(puntos_mapa)

