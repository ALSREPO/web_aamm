import logging
import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID

logger = logging.getLogger("AAMM-APP-TELEGRAM-NOTIFICADOR")


# A partir de un mail, un nombre y el id del usuario, envía una solicitud al admin para aprobar o denegar el registro del usuario
def enviar_solicitud_registro_telegram(email: str, nombre: str, idusuario: int):
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
                {"text": "✅ Aprobar", "callback_data": f"aprobar:{idusuario}"},
                {"text": "❌ Denegar", "callback_data": f"denegar:{idusuario}"}
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
        logger.info(f"Solicitud de activación enviada a Telegram para el usuario ID_USUARIO[{idusuario}]")
    except Exception as e:
        logger.error(f"Error al enviar la solicitud de activación a Telegram para el usuario ID_USUARIO[{idusuario}]: {e}")


# incluir en el fichero config del bot de telegram:
"""
API_BASE_URL = "https://aamm_develop.alsdev.com/api"
TELEGRAM_BOT_API_KEY="pass" # la misma que en el .env/YAML de FastAPI, necesaria para autenticar la llamada desde el bot al endpoint de cambio de estatus
"""
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

    # 2. Extraer la acción y el ID de usuario del callback_data
    accion, idusuario = call.data.split(":", 1)
    
    # 3. Mapeamos la acción de Telegram con los estados reales de tu API
    # 1 = Activar, 0 = Banear/Denegar
    nuevo_estado = 1 if accion == "aprobar" else 0
    
    # Construimos la URL exacta apuntando a tu nuevo endpoint
    url_api = f"{API_BASE_URL}/usuarios/cambiar-estatus-bot/{idusuario}"
    
    # Parámetros que espera recibir tu endpoint (estado)
    params = {"estado": nuevo_estado}
    
    # 🛠️ IMPORTANTE: Si tu endpoint pide token de administrador por cabecera, 
    # añade aquí las credenciales. Si no las pide, puedes borrar la variable headers.
    headers = {
        "X-Telegram-Bot-Key": TELEGRAM_BOT_API_KEY # La misma del .env
    }

    try:
        # Hacemos la llamada HTTP PATCH a FastAPI
        # Si no usas seguridad en este endpoint específico, quita el parámetro: headers=headers
        response = requests.patch(url_api, params=params, headers=headers, timeout=10, verify=False)
        
        # Si la API responde con un código 2xx (Éxito)
        if response.status_code == 200:
            
            if accion == "aprobar":
                texto_editated = f"✅ *Cuenta Activada Exitosamente*\n🆔 ID Usuario: `{idusuario}`\n\n_Acción procesada vía API y notificada por correo._"
                alerta_pop_up = "Usuario aprobado con éxito"
                print(f"API: Se aprueba al usuario ID {idusuario}")
            else:
                texto_editated = f"❌ *Cuenta Denegada/Bloqueada*\n🆔 ID Usuario: `{idusuario}`\n\n_Acción procesada vía API._"
                alerta_pop_up = "Usuario rechazado"
                print(f"API: Se deniega al usuario ID {idusuario}")

            # 4. Modificar el mensaje original en Telegram para deshabilitar botones
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text=texto_editated,
                parse_mode="Markdown",
                reply_markup=None # Quitamos los botones para evitar doble clic
            )
            
            # 5. Notificación flotante de éxito en la app de Telegram
            bot.answer_callback_query(call.id, alerta_pop_up)
            
        else:
            # Si la API encuentra un error (Ej: 404 No encontrado, 401 No autorizado)
            error_detail = response.json().get("detail", "Error desconocido")
            print(f"Error devuelto por la API [{response.status_code}]: {error_detail}")
            bot.answer_callback_query(call.id, f"❌ Error API ({response.status_code}): {error_detail}", show_alert=True)

    except requests.exceptions.RequestException as e:
        # Controlamos si el servidor FastAPI está caído o no responde
        print(f"Error de conexión con la API de FastAPI: {e}")
        bot.answer_callback_query(call.id, "🔌 No se pudo conectar con el servidor de la API", show_alert=True)

"""