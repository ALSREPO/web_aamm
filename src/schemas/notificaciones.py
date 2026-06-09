from pydantic import BaseModel, Field
from typing import Optional

class PreferenciaNotificacionSchema(BaseModel):
    """Esquema para enviarle las preferencias actuales al frontend"""
    nombre_clave: str = Field(..., example="nuevo_video")
    nombre_pantalla: str = Field(..., example="Nuevos vídeos de entrenamiento")
    descripcion: Optional[str] = Field(None, example="Te avisamos cuando se suba contenido nuevo.")
    canal_push: bool = Field(True, description="Estado de las notificaciones Web Push")
    canal_email: bool = Field(False, description="Estado de las notificaciones por Correo")

    class Config:
        from_attributes = True  # Permite leer directamente objetos de SQLAlchemy


class ActualizarPreferenciaSchema(BaseModel):
    """Esquema que recibimos del frontend cuando cambian un checkbox"""
    nombre_clave: str = Field(..., example="nuevo_video")
    canal: str = Field(..., description="Debe ser 'push' o 'email'")
    valor: bool = Field(..., description="True para activar, False para desactivar")