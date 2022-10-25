import os

import streamlit as st
import pandas as pd

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from crea_db import CargasBip

# Esto solo para hacer referencia a una base de datos SQLlite local:
ruta_mi_bd = os.path.abspath("./cargas.db")
mi_bd = f"sqlite:///{ruta_mi_bd}"

# Crear conexión a BD
# Se quita el parámetro "future=True", por compatibilidad con Pandas 1.x
engine = create_engine(mi_bd)
# Crear sesión a BD
session = Session(engine)

# Consultar por registros de algunas comunas
sql_comuna = select(CargasBip).where(CargasBip.COMUNA.in_(["PROVIDENCIA", "SANTIAGO", "LA FLORIDA"]) )
sql_comuna = sql_comuna.order_by(CargasBip.COMUNA)
# Obtener todos los registros de la consulta
registros_comuna = session.scalars(sql_comuna).all()

# Consultar registros directo desde Pandas
datos_comunas = pd.read_sql_query(sql=sql_comuna, con=engine, index_col="CODIGO")

# Configurar Aplicación
st.set_page_config(
  layout="wide"
)

# Mostrar datos en la Aplicación
st.header("Información desde Base de Datos")

st.info("Puntos de Carga")
st.write(datos_comunas)
