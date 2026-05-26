from passlib.context import CryptContext
from src.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from src.models.models import Usuario
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from src.utils.db_tools import get_read_db


# Configuración de Passlib para usar SHA-512
# 'crypt_dist' asegura que usemos implementaciones seguras
pwd_context = CryptContext(schemes=["sha512_crypt"], deprecated="auto")



def verificar_password(plain_password, hashed_password):
    """Compara la contraseña en plano con el hash de la BBDD"""
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password):
    """Genera el hash SHA-512 de una contraseña"""
    return pwd_context.hash(password)

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    """Genera un token JWT firmado"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Una vez iniciada sesion, crear y validar el token que viene desde la cookie
def obtener_token_de_cookie(request: Request):
    """
    Extrae el token JWT de la cookie llamada 'access_token'.
    """
    return request.cookies.get("access_token")

def validar_token(token: str):
    """
    Decodifica y valida el token. Devuelve el email si es válido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def crear_token_verificacion(email: str):
    expiracion = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": email, "exp": expiracion, "purpose": "email_verification"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Pendiente de desarrollar el envío de correo
def enviar_correo_verificacion(email_destino: str, token: str):
    return True

async def obtener_usuario_actual(request: Request, db: Session = Depends(get_read_db)):
    token = obtener_token_de_cookie(request)
    if not token:
        return None
    
    email = validar_token(token)
    if not email:
        return None
        
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or user.activo < 1:
        return None
    return user 

async def verificar_admin(user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador"
        )
    return user