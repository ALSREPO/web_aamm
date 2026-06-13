import json
import os
import logging
import traceback
import pywebpush
from pywebpush import webpush, WebPushException
from py_vapid import Vapid
from cryptography.hazmat.primitives.asymmetric import ec
from src.config import VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, EMAIL_EMISOR as VAPID_ADMIN_EMAIL
from sqlalchemy.orm import Session

# Workaround para pywebpush con cryptography >= 41.
# pywebpush llama a `ec.generate_private_key(ec.SECP256R1, ...)`,
# pero la API moderna requiere una instancia de curva.
if hasattr(pywebpush, "ec") and hasattr(pywebpush.ec, "generate_private_key"):
    _orig_generate_private_key = pywebpush.ec.generate_private_key

    def _wrapped_generate_private_key(curve, backend=None):
        if isinstance(curve, type) and issubclass(curve, ec.EllipticCurve):
            curve = curve()
        return _orig_generate_private_key(curve, backend)

    pywebpush.ec.generate_private_key = _wrapped_generate_private_key

logger = logging.getLogger("aamm")


def enviar_notificacion_push(suscripcion_db, titulo: str, cuerpo: str, ruta_destino: str = None, db: Session = None) -> bool:
    """
    Toma una suscripción de la base de datos, cifra el mensaje y lo envía
    al servidor push del navegador. Si el token expiró (410 Gone), lo borra automáticamente.
    """
    # 1. Inicializamos las variables arriba para evitar problemas de scope 🌟
    endpoint = None
    p256dh = None
    auth = None

    # 2. Extraemos los datos de forma segura (sirve para objetos SQLAlchemy y diccionarios)
    try:
        endpoint = getattr(suscripcion_db, 'endpoint', None) or suscripcion_db.get('endpoint')
        p256dh = getattr(suscripcion_db, 'p256dh', None) or suscripcion_db.get('p256dh')
        auth = getattr(suscripcion_db, 'auth', None) or suscripcion_db.get('auth')
    except Exception as e:
        logger.error(f"Error al parsear el objeto de suscripción: {e}")
        return False

    if not endpoint or not p256dh or not auth:
        logger.error("Faltan campos obligatorios (endpoint, p256dh o auth) para enviar el push.")
        return False

    # 3. Montamos la estructura que exige pywebpush
    info_suscripcion = {
        "endpoint": endpoint,
        "keys": {
            "p256dh": p256dh,
            "auth": auth
        }
    }

    # 4. Preparamos el paquete de datos que leerá el Service Worker
    datos_mensaje = {
        "notification": {
            "title": titulo,
            "body": cuerpo,
            "icon": "/static/favicon.ico",
            "badge": "/static/favicon.ico",
            "tag": "alerta-escuela",  # MISMO TAG: El navegador machaca la anterior si hay duplicados
            "renotify": True,        # Hacer que vibre/suene al actualizarse aunque tenga el mismo tag
            "data": {
                "url": ruta_destino or "/"
            }
        }
    }

    # 5. Envío criptográfico
    try:
        logger.info("Enviando notificación push usando claves VAPID explícitas.")

        vapid_key = VAPID_PRIVATE_KEY
        if vapid_key:
            vapid_key = vapid_key.strip().strip('"').strip("'")

        vapid_key_obj = None
        if vapid_key:
            try:
                vapid_key_obj = Vapid.from_string(vapid_key)
            except Exception:
                vapid_key_obj = vapid_key

        webpush(
            subscription_info=info_suscripcion,
            data=json.dumps(datos_mensaje),
            vapid_private_key=vapid_key_obj,
            vapid_claims={"sub": f"mailto:{VAPID_ADMIN_EMAIL}"}
        )
        return True

    except WebPushException as ex:
        # 🌟 MODIFICACIÓN AQUÍ: Captura y limpieza silenciosa del 410/404 Gone
        status_code = ex.response.status_code if ex.response else None
        
        if status_code in [410, 404] or "Gone" in ex.message:
            id_usuario = getattr(suscripcion_db, 'idusuario', 'Desconocido')
            logger.warning(f"[Push] El token ya no es válido (Código {status_code}). Limpiando dispositivo obsoleto del usuario ID: {id_usuario}")
            
            # Si tenemos la sesión de base de datos activa y es un objeto de SQLAlchemy, lo borramos 🧹
            if db and hasattr(suscripcion_db, '_sa_instance_state'):
                try:
                    db.delete(suscripcion_db)
                    db.commit()
                    logger.info(f"[Push] Registro eliminado correctamente de MySQL.")
                except Exception as db_err:
                    db.rollback()
                    logger.error(f"[Push] Error al intentar borrar el token de MySQL: {db_err}")
            return False

        # Si es otro error de WebPush diferente a un token revocado, sí dejamos el log de error
        logger.error(f"Error en el servidor Push externo (WebPushException): {ex}\n{traceback.format_exc()}")
        return False

    except Exception as e:
        logger.error(f"Error crítico en el envío de la notificación push: {e}\n{traceback.format_exc()}")
        return False