import logging

from passlib.context import CryptContext
from src.config import SECRET_KEY, ALGORITHM, EMAIL_EMISOR, BASE_URL, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from src.models.models import Usuario
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from src.utils.db_tools import get_read_db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de Passlib para usar SHA-512
# 'crypt_dist' asegura que usemos implementaciones seguras
pwd_context = CryptContext(schemes=["sha512_crypt"], deprecated="auto")

logger = logging.getLogger("AAMM-APP-auth")


def verificar_password(plain_password, hashed_password):
    """Compara la contraseña en plano con el hash de la BBDD"""
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password):
    """Genera el hash SHA-512 de una contraseña"""
    return pwd_context.hash(password)

from datetime import datetime, timezone, timedelta
from typing import Optional

def crear_token_acceso(data: dict, expires_at: Optional[datetime] = None):
    """Genera un token JWT firmado usando una fecha de expiración absoluta"""
    to_encode = data.copy()
    
    if expires_at:
        # Si le pasamos la fecha final desde el login, la usamos directamente
        expire = expires_at
    else:
        # Por si acaso se llama desde otro sitio sin fecha, le damos 15 minutos por defecto
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
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


def verificar_token_verificacion(token: str):
    # O simplemente usa las excepciones de jose.jwt directamente:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificamos que el propósito del token sea el correcto
        if payload.get("purpose") != "email_verification":
            return None
            
        return payload.get("sub") # Retorna el email

    except jwt.ExpiredSignatureError:
        return None # Token caducado
        
    except jwt.JWTError: 
        return None # Token inválido, firma falsa o manipulada


def enviar_correo_verificacion(email_destino: str, token: str):
    # 1. Configuración de credenciales de correo
    smtp_server     = SMTP_SERVER     # smtp-relay.brevo.com
    smtp_port       = SMTP_PORT       # 587
    smtp_usuario    = SMTP_USERNAME   # Tu login de Brevo
    smtp_password   = SMTP_PASSWORD   # La contraseña SMTP que generaste
    
    emisor          = EMAIL_EMISOR    # no-reply@alsdev.com
    base_url        = BASE_URL        # Ejemplo: https://midominio.com

    enlace = f"{base_url}/verificar_mail?token={token}"

    # 2. Creación del mensaje estructurado
    mensaje = MIMEMultipart("alternative")
    mensaje["From"] = emisor
    mensaje["To"] = email_destino
    mensaje["Subject"] = "Verifica tu cuenta en la web AAMM"

    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
        <h2 style="color: #333;">¡Bienvenido a la web de Artes Marciales!</h2>
        <p>Para terminar tu registro, por favor confirma tu dirección de correo electrónico pulsando el siguiente botón:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{enlace}" style="background-color: #10b981; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verificar Correo</a>
        </div>
        <p style="font-size: 12px; color: #666;">Si el botón no funciona, copia y pega este enlace en tu navegador:<br>{enlace}</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #999;">Este enlace caducará en 24 horas. Si no te has registrado tú, puedes ignorar este correo.</p>
    </div>
    """
    
    # Acoplamos el contenido HTML al mensaje
    mensaje.attach(MIMEText(html_content, "html"))

    # 3. Envío seguro a través del servidor SMTP de Brevo
    try:
        # Conectamos al servidor usando TLS (Puerto 587)
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()  # Ciframos la conexión de forma segura
        server.login(smtp_usuario, smtp_password)
        
        # Enviamos el correo
        server.sendmail(emisor, email_destino, mensaje.as_string())
        server.quit()
        return True
    except Exception as e:
        logger.error(f"Error enviando correo a través de Brevo SMTP - {email_destino}: {e}")
        return False



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
        logger.warning(f"Intento de acceso no autorizado a ruta admin por parte de {user.email if user else 'usuario desconocido'}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador"
        )
    return user


async def usuario_obligatorio(user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 1:
        logger.warning(f"Intento de acceso no autorizado por parte de {user.email if user else 'usuario desconocido'}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requiere estar logueado"
        )
    return user

