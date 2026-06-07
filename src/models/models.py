from sqlalchemy import Column, Integer, String, Date,  Text, ForeignKey, Table, Boolean, select, func
from sqlalchemy.orm import relationship, column_property
from src.utils.db_tools import Base


# --- Tablas de Asociación (Muchos a Muchos) ---

tecnicas_disciplinas = Table(
    'ta_tecnicas_disciplinas', Base.metadata,
    Column('iddisciplina', Integer, ForeignKey('ta_disciplinas.iddisciplina'), primary_key=True),
    Column('idtecnica', Integer, ForeignKey('ta_tecnicas.idtecnica'), primary_key=True)
)

tecnicas_etiquetas = Table(
    'ta_tecnicas_etiquetas', Base.metadata,
    Column('idetiqueta', Integer, ForeignKey('ta_etiquetas.idetiqueta'), primary_key=True),
    Column('idtecnica', Integer, ForeignKey('ta_tecnicas.idtecnica'), primary_key=True)
)


# --- Clases Principales ---

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



class Disciplina(Base):
    __tablename__ = "ta_disciplinas"
    iddisciplina = Column(Integer, primary_key=True, autoincrement=True)
    disciplina = Column(String(255), nullable=False)

class Etiqueta(Base):
    __tablename__ = "ta_etiquetas"
    idetiqueta = Column(Integer, primary_key=True, autoincrement=True)
    etiqueta = Column(String(255), nullable=False)
    orden = Column(Integer, nullable=False, default=999999)

class Video(Base):
    __tablename__ = "ta_tecnicas_videos"
    idvideo = Column(Integer, primary_key=True, autoincrement=True)
    video = Column(String(500), nullable=False)
    idtecnica = Column(Integer, ForeignKey('ta_tecnicas.idtecnica'), primary_key=True)


class Tecnica(Base):
    __tablename__ = "ta_tecnicas"
    idtecnica = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)

    # Relaciones
    videos = relationship("Video", backref="tecnica", cascade="all, delete-orphan")
    etiquetas = relationship("Etiqueta", secondary=tecnicas_etiquetas, backref="tecnicas", order_by="Etiqueta.orden")
    disciplinas = relationship("Disciplina", secondary=tecnicas_disciplinas, backref="tecnicas")

    # COLUMNA CALCULADA: Conteo de vídeos
    # Esta subconsulta cuenta cuántos registros hay en ta_tecnicas_videos para esta técnica
    cantidad_videos = column_property(
        select(func.count(Video.idvideo))
        .where(Video.idtecnica == idtecnica)
        .correlate_except(Video)
        .scalar_subquery()
    )
