from pydantic import BaseModel, HttpUrl

class KeysSchema(BaseModel):
    p256dh: str
    auth: str

class SuscripcionPushSchema(BaseModel):
    endpoint: str  # Lo dejamos como str porque las URLs de los servidores push de Google/Apple pueden ser extremadamente largas
    keys: KeysSchema

    class Config:
        from_attributes = True  # Esto es el antiguo 'orm_mode = True' de Pydantic v1, para que sea compatible con SQLAlchemy

"""
# Documentación de la API del navegador, un objeto de suscripción push tiene siempre esta forma
{
  "endpoint": "https://fcm.googleapis.com/fcm/send/eXamplE...",
  "keys": {
    "p256dh": "BLm...cadena_criptografica...",
    "auth": "BTz...token_de_autenticacion..."
  }
}
"""