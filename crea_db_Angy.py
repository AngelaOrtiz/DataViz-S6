import pandas as pd
import os
import random
from numpy import NaN, append, identity, unicode_
import pydeck as pdk
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components

# Leer Excel
bip = pd.read_excel("carga-bip.xlsx", header=9)
# Corregir nombres de columnas
bip.rename(columns={
  "NOMBRE FANTASIA": "NOMBRE_FANTASIA",
  "CERRO BLANCO 625": "DIRECCION",
  "MAIPU": "COMUNA",
  "HORARIO REFERENCIAL": "HORARIO_REFERENCIAL"
}, inplace=True)

#Elimina registros de comuna que no posee dato
bip.dropna(subset=["COMUNA"], inplace=True)

#Asigna aleatoriamente horarios a los puntos de carga
horarios = ["09:00 - 13:00, 14:00 -19:00","08:00 - 13:30, 14:30 -21:00","08:30 - 13:30, 15:00 -20:00","09:30 - 13:00, 15:00 -22:00","10:00 - 13:00, 14:00 -24:00"]
for i in range (0,len(bip)):
    bip["HORARIO_REFERENCIAL"] = bip["HORARIO_REFERENCIAL"].apply(lambda x: horarios[random.randint(0,len(horarios)-1)])


#Crea lista de comunas a partir de Excel
listaComuna=bip['COMUNA'].to_list()
comunas=[]
for n in listaComuna:
    if n not in comunas:
        if n is not NaN:
            comunas.append(n)
print(comunas)

################################################################################################
st.set_page_config(
  page_icon=":thumbs_up:",
  layout="wide",
  )

st.header("Puntos de carga BIP!")
st.info("Metro de santiago")

components.html("""
<iframe width="560" height="315" src="https://www.youtube.com/embed/ckXpOmQIW4o" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
""",600,300)

st.info("Mapa de puntos de carga")
col_sel, col_map = st.columns([1,2])

with st.sidebar:
  horarios_seleccionados = st.multiselect(
    label="Filtrar por horario de atención", 
    options=horarios,
    help="Selecciona los horarios a mostrar",
    default=[] # También se puede indicar la variable "comunas", para llenar el listado
  )

geo_data = bip

# Aplicar filtro de Horarios
if horarios_seleccionados:
  geo_data = bip.query("HORARIO_REFERENCIAL == @horarios_seleccionados")

st.sidebar.write(geo_data.set_index("CODIGO"))


# Obtener el punto promedio entre todas las georeferencias
avg_lat = np.average(geo_data["LATITUD"])
avg_lng = np.average(geo_data["LONGITUD"])

puntos_mapa = pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=avg_lat,
        longitude=avg_lng,
        zoom=10,
        pitch=20,
    ),
    layers=[
      pdk.Layer(
        "ScatterplotLayer",
        data = geo_data,
        pickable=True,
        get_position='[LONGITUD, LATITUD]',
        opacity=0.8,
        filled=True,
        radius_scale=2,
        radius_min_pixels=5,
        radius_max_pixels=50,
        line_width_min_pixels=0.01,
        get_fill_color=["HORARIO_REFERENCIAL== '09:00 - 13:00, 14:00 -19:00'? 210:10","HORARIO_REFERENCIAL== '08:30 - 13:30, 15:00 -20:00'? 0:180","HORARIO_REFERENCIAL== '09:30 - 13:00, 15:00 -22:00'? 30:255",200]
      )      
    ],
    tooltip={
      "html": "<b>Negocio: </b> {NOMBRE_FANTASIA} <br /> "
              "<b>Dirección: </b> {DIRECCION} <br /> "
              "<b>Comuna: </b> {COMUNA} <br /> "
              "<b>Código: </b> {CODIGO} <br /> "
              "<b>Horario de atención: </b> {HORARIO_REFERENCIAL} <br /> "
              "<b>Georeferencia (Lat, Lng): </b>[{LATITUD}, {LONGITUD}] <br /> "
    }
)

st.write(puntos_mapa)
