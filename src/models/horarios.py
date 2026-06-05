from sqlalchemy import Column, Integer, String, Time
from src.utils.db_tools import Base

class HorarioClase(Base):
    __tablename__ = "ta_horarios"

    idhorario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    actividad = Column(String(100), nullable=False)
    dia_semana = Column(Integer, nullable=False)  # 1=Lunes, 2=Martes...
    hora_inicio = Column(Time, nullable=False)    # Almacena objetos datetime.time nativos
    hora_fin = Column(Time, nullable=False)       # Almacena objetos datetime.time nativos
