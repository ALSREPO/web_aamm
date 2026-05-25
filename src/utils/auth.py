from passlib.context import CryptContext
from src.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

# Configuración de Passlib para usar SHA-512
# 'crypt_dist' asegura que usemos implementaciones seguras
pwd_context = CryptContext(schemes=["sha512_crypt"], deprecated="auto")



def verificar_password(plain_password, hashed_password):
    """Compara la contraseña en plano con el hash de la BBDD"""
    return pwd_context.verify(plain_password, hashed_password)


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