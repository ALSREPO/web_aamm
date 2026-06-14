from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, text
from sqlalchemy.dialects.mysql import MEDIUMINT, TINYINT, INTEGER
from sqlalchemy.orm import relationship
from datetime import datetime
from src.utils.db_tools import Base  # Ajusta la ruta a tu declaración de Base

class NotificacionTipo(Base):
    __tablename__ = "notificaciones_tipos"

    # Usamos TINYINT UNSIGNED para ID pequeños (hasta 255 tipos de eventos)
    idtipo = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=True)
    nombre_clave = Column(String(50), unique=True, nullable=False, index=True)
    nombre_pantalla = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    # Relación para acceder a las configuraciones desde el tipo de evento si hiciera falta
    configuraciones = relationship("UsuarioNotificacionConfig", back_populates="tipo_evento", cascade="all, delete-orphan")


class UsuarioNotificacionConfig(Base):
    __tablename__ = "usuarios_notificaciones_config"

    idconfig = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True) 
    
    # 🌟 CLAVE FORÁNEA EXACTA: MEDIUMINT UNSIGNED apuntando a ta_usuarios
    idusuario = Column(
        MEDIUMINT(unsigned=True), 
        ForeignKey("ta_usuarios.idusuario", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Clave foránea que apunta a nuestro catálogo
    idtipo = Column(
        TINYINT(unsigned=True), 
        ForeignKey("notificaciones_tipos.idtipo", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Canales de alertas
    canal_push = Column(Boolean, default=True, nullable=False)
    canal_email = Column(Boolean, default=False, nullable=False)
    
    # Timestamp automático de MySQL para control de actualizaciones
    actualizado_en = Column(
        DateTime, 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

    # Relación ORM para hacer consultas limpias del tipo: config.tipo_evento.nombre_pantalla
    tipo_evento = relationship("NotificacionTipo", back_populates="configuraciones")