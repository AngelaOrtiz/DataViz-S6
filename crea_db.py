import pandas as pd
import os
from sqlalchemy import Column, Float, Integer, String, create_engine, select
from sqlalchemy.orm import declarative_base, Session

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
bip = pd.read_excel("carga-bip.xlsx", header=9, index_col="CODIGO")
# Corregir nombres de columnas
bip.rename(columns={
  "NOMBRE FANTASIA": "NOMBRE_FANTASIA",
  "CERRO BLANCO 625": "DIRECCION",
  "MAIPU": "COMUNA",
  "HORARIO REFERENCIAL": "HORARIO_REFERENCIAL"
}, inplace=True)

# Grabar DataFrame en BD
bip.to_sql(con=engine, name="cargasbip", if_exists="replace", index_label="CODIGO")

# Crear sesión a BD
session = Session(engine)

# Consultar por registros de algunas comunas
sql_comuna = select(CargasBip).where(CargasBip.COMUNA.in_(["RENCA", "ÑUÑOA"]) )
registros_comuna = session.scalars(sql_comuna).all()
for punto_carga in registros_comuna:
  print(punto_carga)


def formato_porciento(dato: float):
  return f"{round(dato, ndigits=2)}%"