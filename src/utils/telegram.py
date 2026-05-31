import logging
import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID

logger = logging.getLogger("AAMM-APP-TELEGRAM-NOTIFICADOR")

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