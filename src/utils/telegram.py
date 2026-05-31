import logging
import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID

logger = logging.getLogger("AAMM-APP-TELEGRAM-NOTIFICADOR")

# Solo envía mensajes al Administrador del bot de Telegram
def enviar_alerta_telegram(mensaje: str):
    """Envía un mensaje de notificación al administrador a través de un Bot de Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        logger.warning("Telegram no configurado: Faltan variables de entorno.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"  # Permite usar negritas, emojis, etc.
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            logger.error(f"Error de Telegram API: {response.text}")
    except Exception as e:
        logger.error(f"No se pudo enviar la alerta de Telegram: {e}")


# A partir de un mail y un nombre, envía una solicitud al admin para aprobar o denegar el registro del usuario
def enviar_solicitud_registro_telegram(email: str, nombre: str):
    """Envía una alerta al admin con botones interactivos para activar/denegar al usuario"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        logger.warning("Telegram no configurado.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Texto informativo para el Admin
    texto = (
        "🆕 *¡Nueva solicitud de registro en la Web!*\n\n"
        f"👤 *Nombre:* {nombre}\n"
        f"📧 *Correo:* `{email}`\n\n"
        "¿Deseas activar esta cuenta para la biblioteca?"
    )

    # Estructura de los botones interactivos (Inline Keyboard)
    # Importante: Guardamos la acción y el email en el callback_data
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Aprobar", "callback_data": f"aprobar:{email}"},
                {"text": "❌ Denegar", "callback_data": f"denegar:{email}"}
            ]
        ]
    }

    payload = {
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown",
        "reply_markup": inline_keyboard  # Adjuntamos los botones
    }

    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Error al enviar botones a Telegram: {e}")