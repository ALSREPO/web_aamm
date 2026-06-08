from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from src.models.models import Base  # O la ruta exacta donde importes tu declarative_base

class SuscripcionPush(Base):
    __tablename__ = "suscripciones_push"

    id = Column(Integer, primary_key=True, autoincremental=True)
    idusuario = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    endpoint = Column(Text, nullable=False)
    p256dh = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)
    creado_en = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relación opcional por si desde el usuario quieres consultar sus dispositivos
    usuario = relationship("Usuario", back_populates="suscripciones_push")