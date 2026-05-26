from passlib.context import CryptContext
from src.config import SECRET_KEY, ALGORITHM, EMAIL_EMISOR, BASE_URL, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
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


def enviar_correo_verificacion(email_destino: str, token: str):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # 1. Configuración de credenciales (Sustituye por tus variables o strings)
    # Recomiendo guardar BREVO_SMTP_PASSWORD en tus variables de entorno (.env)
    smtp_server = SMTP_SERVER  # smtp-relay.brevo.com
    smtp_port = SMTP_PORT      # 587
    smtp_usuario = SMTP_USERNAME  # Tu login de Brevo
    smtp_password = SMTP_PASSWORD   # La contraseña SMTP que generaste
    
    emisor = EMAIL_EMISOR  # no-reply@alsdev.com
    base_url = BASE_URL    # Ejemplo: https://midominio.com

    enlace = f"{base_url}/api/autenticacion/verificar?token={token}"

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
        print(f"Error enviando correo a través de Brevo SMTP: {e}")
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador"
        )
    return user