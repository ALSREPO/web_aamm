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
            logger.error(f"Error de Telegram API, para el usuario ID_USUARIO[{nombre}]: {response.text}")
    except Exception as e:
        logger.error(f"No se pudo enviar la alerta de Telegram, para el usuario ID_USUARIO[{nombre}]: {e}")


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
        logger.info(f"Solicitud de activación enviada a Telegram para el usuario ID_USUARIO[{nombre}]")
    except Exception as e:
        logger.error(f"Error al enviar la solicitud de activación a Telegram para el usuario ID_USUARIO[{nombre}]: {e}")


# Incluir en el bot de Telegram un manejador para los callbacks de los botones (Aprobar/Denegar) que actualice la base de datos y edite el mensaje original para reflejar la acción tomada. Esto se hace en el script del bot, no en FastAPI, pero es crucial para cerrar el ciclo de interacción.
"""
# MANEJADOR PARA LOS BOTONES INTERACTIVOS (Aprobar / Denegar)
@bot.callback_query_handler(func=lambda call: call.data.startswith(('aprobar:', 'denegar:')))
def callback_gestion_usuarios(call):
    
    cid = call.from_user.id
    # 1. Comprobar que quien pulsa el botón es el administrador real
    # Cambia CHAT_ID_ADMIN por tu variable de ID de administrador
    if not es_admin(cid, False):
        return

    # 2. Extraer la acción y el email del callback_data
    accion, email = call.data.split(":", 1)
    
    # 3. Conectamos a la base de datos de tu proyecto FastAPI actual
    # NOTA: Adapta "obtener_conexion_fastapi()" a cómo te conectes en tu script del bot
    try:
        with obtener_conexion() as db:
            with db.cursor() as cursor:
                if accion == "aprobar":
                    # Cambiamos activo a True (o 1) buscando por email
                    cursor.execute("UPDATE ta_usuarios SET activo = 1 WHERE email = %s", (email,))
                    db.commit()
                    
                    texto_editado = f"✅ *Cuenta Activada Exitosamente*\n📧 Correo: `{email}`\n\n_Acción procesada por el Administrador._"
                    alerta_pop_up = "Usuario aprobado con éxito"
                    print(f"Se aprueba la solicitud de {email}")
                    
                elif accion == "denegar":
                    # Si se deniega, podemos optar por borrarlo o dejarlo inactivo (activo=False)
                    # En este ejemplo lo dejamos Inactivo permanentemente
                    cursor.execute("UPDATE ta_usuarios SET activo = -1 WHERE email = %s", (email,))
                    db.commit()
                    
                    texto_editado = f"❌ *Cuenta Denegada/Bloqueada*\n📧 Correo: `{email}`\n\n_Acción procesada por el Administrador._"
                    alerta_pop_up = "Usuario rechazado"
                    print(f"Se rechaza la solicitud de {email}")

        # 4. Modificar el mensaje original en Telegram para quitar los botones 
        # y dejar constancia de que ya se ha pulsado. ¡Evita que se pulse dos veces!
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=texto_editado,
            parse_mode="Markdown",
            reply_markup=None # Quitamos los botones
        )
        
        # 5. Notificación flotante rápida en la pantalla de Telegram del administrador
        bot.answer_callback_query(call.id, alerta_pop_up)

    except Exception as e:
        print(f"Error en BBDD al procesar Telegram Callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error interno en la Base de Datos", show_alert=True)

"""