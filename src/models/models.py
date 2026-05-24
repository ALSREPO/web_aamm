from sqlalchemy import Column, Integer, String, Date, Boolean
from src.utils.db_tools import Base

class Usuario(Base):
    __tablename__ = "ta_usuarios"
    idusuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    password = Column(String(200), nullable=False)
    fechaCreacion = Column(Date, nullable=False)
    email = Column(String(60), nullable=False, default="na@na.com")
    activo = Column(Integer, nullable=False, default=0)
    tchatid = Column(String(15))
    tchatusername = Column(String(100))
    tchatfirst_name = Column(String(100))
    tchatlast_name = Column(String(100))
    email_verificado = Column(Boolean, default=False)
