from turtle import home
import pandas as pd
import os
import random
from sqlalchemy import Column, Float, Integer, String, create_engine, select
from sqlalchemy.orm import declarative_base, Session
from numpy import NaN, append, identity, unicode_
import pydeck as pdk
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Esto solo para hacer referencia a una base de datos SQLlite local:
ruta_mi_bd = os.path.abspath("./cargas.db")
mi_bd = f"sqlite:///{ruta_mi_bd}"
# En caso de ser una base de datos PostgreSQL, el formato sería:
# mi_bd = f"postgres://usuario:clave@servidor/base_de_datos"

# Conectar a la BD
# El parámetro echo=True, muestra en consola lo que genera SQLAlchemy
# El parámetro future=True, activa las funcionalidades de la versión 2.x
engine = create_engine(mi_bd, echo=True, future=True)

# Crear clase de Modelo de Datos SQLAlchemy
Base = declarative_base()

# Crear clase de Modelo de la tabla a usar
class CargasBip(Base):
  # Nombre de la tabla
  __tablename__ = "cargasbip"

  # Definir cada atributo de la tabla y su tipo de dato
  CODIGO = Column(Integer, primary_key=True)
  ENTIDAD = Column(String(100))
  NOMBRE_FANTASIA = Column(String(100))
  DIRECCION = Column(String(100))
  COMUNA = Column(String(100))
  HORARIO_REFERENCIAL = Column(String(100))
  ESTE = Column(Integer)
  NORTE = Column(Integer)
  LONGITUD = Column(Float)
  LATITUD = Column(Float)

  def __repr__(self) -> str:
    return f" CargasBip(CODIGO={self.CODIGO}, ENTIDAD={self.ENTIDAD}, NOMBRE_FANTASIA={self.NOMBRE_FANTASIA}, " \
      + f"DIRECCION={self.DIRECCION}, COMUNA={self.COMUNA}, HORARIO_REFERENCIAL={self.HORARIO_REFERENCIAL}," \
      + f"ESTE={self.ESTE}, NORTE={self.NORTE}, LONGITUD={self.LONGITUD}, LATITUD={self.LATITUD}" \
      + ")"

# Crear la tabla en BD
Base.metadata.create_all(engine)

# Leer Excel
bip = pd.read_excel("carga-bip.xlsx", header=9)
# Corregir nombres de columnas
bip.rename(columns={
  "NOMBRE FANTASIA": "NOMBRE_FANTASIA",
  "CERRO BLANCO 625": "DIRECCION",
  "MAIPU": "COMUNA",
  "HORARIO REFERENCIAL": "HORARIO_REFERENCIAL"
}, inplace=True)

#Asigna aleatoriamente horarios a los puntos de carga
horarios = ["09:00 - 13:00, 14:00 -19:00","08:00 - 13:30, 14:30 -21:00","08:30 - 13:30, 15:00 -20:00","09:30 - 13:00, 15:00 -22:00","10:00 - 13:00, 14:00 -24:00"]
for i in range (0,len(bip)):
    bip["HORARIO_REFERENCIAL"] = bip["HORARIO_REFERENCIAL"].apply(lambda x: horarios[random.randint(0,len(horarios)-1)])

bip.dropna(subset=["COMUNA"], inplace=True)
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

st.header("Mini-Desafio de Visualizaciones")
st.info("##### Agrupa por horario")

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
