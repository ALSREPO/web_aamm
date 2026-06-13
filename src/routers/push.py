import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.utils.db_tools import get_write_db
from src.utils.auth import usuario_obligatorio  # Ajusta esta ruta a tu sistema de protección de rutas
from src.models.push import SuscripcionPush
from src.schemas.push import SuscripcionPushSchema
from src.utils.push_notifications import enviar_notificacion_push
from src.config import ENTORNO

logger = logging.getLogger("aamm")

router = APIRouter(
    prefix="/api/push",
    tags=["Push Notifications"]
)

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
def guardar_suscripcion(
    suscripcion_in: SuscripcionPushSchema,
    db: Session = Depends(get_write_db),
    current_user = Depends(usuario_obligatorio)
):
    """
    Guarda o actualiza el endpoint de notificación push de un alumno en la BBDD.
    """
    # 1. Buscamos si el dispositivo ya existía en la base de datos
    suscripcion_existente = db.query(SuscripcionPush).filter(
        SuscripcionPush.endpoint == suscripcion_in.endpoint
    ).first()

    if suscripcion_existente:
        # 🌟 SEGURIDAD: Si el dispositivo ya existía pero cambió el alumno (ej: PC compartido), actualizamos el dueño
        if suscripcion_existente.idusuario != current_user.idusuario:
            try:
                suscripcion_existente.idusuario = current_user.idusuario
                # Actualizamos también las claves por si acaso regeneró permisos
                suscripcion_existente.p256dh = suscripcion_in.keys.p256dh
                suscripcion_existente.auth = suscripcion_in.keys.auth
                db.commit()
                logger.info(f"Dispositivo reasignado con éxito al usuario ID: {current_user.idusuario}")
                return {"status": "ok", "message": "Suscripción transferida al usuario actual"}
            except Exception as e:
                db.rollback()
                logger.error(f"Error al reasignar dispositivo en MySQL: {e}")
                raise HTTPException(status_code=500, detail="Error al actualizar el propietario del dispositivo")
        
        # Si el dueño es el mismo, no tocamos nada
        logger.info(f"El usuario {current_user.idusuario} ya tenía registrado este dispositivo. Se omite el guardado.")
        return {"status": "ok", "message": "Dispositivo ya registrado"}

    # 2. Si el dispositivo es completamente nuevo, lo insertamos (Cambiado .id por .idusuario 🌟)
    nueva_suscripcion = SuscripcionPush(
        idusuario=current_user.idusuario, 
        endpoint=suscripcion_in.endpoint,
        p256dh=suscripcion_in.keys.p256dh,
        auth=suscripcion_in.keys.auth
    )
    
    try:
        db.add(nueva_suscripcion)
        db.commit()
        logger.info(f"Nueva suscripción push registrada para el usuario ID: {current_user.idusuario}")
        return {"status": "ok", "message": "Suscripción guardada con éxito"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error al guardar la suscripción push en MySQL: {e}")
        raise HTTPException(status_code=500, detail="No se pudo guardar la suscripción")

if ENTORNO in ["develop"]:
    @router.post("/send-test")
    def enviar_push_prueba(
        db: Session = Depends(get_write_db),
        current_user = Depends(usuario_obligatorio)
    ):
        """
        Ruta temporal de desarrollo para mandarte un push de prueba a todos tus 
        dispositivos registrados.
        """
        # Buscamos todas las suscripciones del usuario que hace la petición
        suscripciones = db.query(SuscripcionPush).filter(SuscripcionPush.idusuario == current_user.idusuario).all()
        
        if not suscripciones:
            raise HTTPException(status_code=404, detail="No tienes ningún dispositivo registrado en este navegador.")

        enviadas_con_exito = 0
        
        for sub in suscripciones:
            # Llamamos a nuestra utilidad de envío
            exito = enviar_notificacion_push(
                suscripcion_db=sub,
                titulo="🥋 Escuela AAMM",
                cuerpo="¡Funciona! Tu servidor FastAPI te acaba de enviar un push en tiempo real.",
                ruta_destino="/perfil",
                db=db
            )
            
            if exito:
                enviadas_con_exito += 1
            else:
                # Si devolvió False es porque el token caducó (Error 410 Gone). Limpiamos la BBDD.
                db.delete(sub)
                db.commit()
                logger.info(f"Limpiando suscripción obsoleta ID {sub.id} del usuario {current_user.idusuario}")

        return {
            "status": "ok", 
            "enviadas": enviadas_con_exito, 
            "limpiadas": len(suscripciones) - enviadas_con_exito
        }