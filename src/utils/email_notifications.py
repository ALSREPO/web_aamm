import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from src.config import (
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, 
    EMAIL_EMISOR, BASE_URL
)

logger = logging.getLogger("AAMM-NOTIFICACION-MAIL")

def enviar_correo_notificacion_evento(email_destino: str, titulo: str, cuerpo: str, ruta_destino: str = None) -> bool:
    """
    Envía un correo electrónico estructurado con las novedades de la escuela vía Brevo SMTP.
    """
    base_url = BASE_URL or "http://localhost:8000"
    enlace = f"{base_url}{ruta_destino}" if ruta_destino else base_url

    mensaje = MIMEMultipart("alternative")
    mensaje["From"] = formataddr(("Escuela de Artes Marciales", EMAIL_EMISOR))
    mensaje["To"] = email_destino
    mensaje["Subject"] = titulo

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            .btn-acceso:hover {{ background-color: #1a47be !important; }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <div style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <div style="background-color: #0f172a; padding: 32px; text-align: center;">
                <span style="font-size: 32px;">🥋</span>
                <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 20px; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase;">Web AAMM</h1>
            </div>
            
            <div style="padding: 32px;">
                <h2 style="color: #1e293b; margin: 0 0 16px 0; font-size: 18px; font-weight: 700;">{titulo}</h2>
                <p style="color: #475569; font-size: 14px; line-height: 1.6; margin: 0 0 24px 0;">{cuerpo}</p>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{enlace}" class="btn-acceso" style="background-color: #1f54de; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 12px; font-weight: bold; font-size: 14px; display: inline-block; transition: background-color 0.2s;">
                        Ver en la plataforma
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
                <p style="font-size: 11px; color: #94a3b8; text-align: center; margin: 0; line-height: 1.5;">
                    Recibes este correo porque tienes activadas las alertas por email en tu perfil de alumno.<br>
                    Puedes cambiar tus preferencias de avisos en cualquier momento desde tu panel de usuario.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    mensaje.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_EMISOR, email_destino, mensaje.as_string())
        server.quit()
        return True
    except Exception as e:
        logger.error(f"[Email] Error enviando correo de novedad a {email_destino}: {e}")
        return False