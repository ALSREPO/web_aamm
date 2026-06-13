# centralizará el envío de cualquier notificación futura

import logging
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from src.models.notificaciones import NotificacionTipo, UsuarioNotificacionConfig
from src.models.push import SuscripcionPush
from src.models.models import Usuario  # Asegúrate de importar tu modelo base de usuarios
from src.utils.push_notifications import enviar_notificacion_push
from src.utils.email_notifications import enviar_correo_notificacion_evento 

logger = logging.getLogger("AAMM-NOTIFICACIONES")

def despachar_notificacion_evento(
    db: Session, 
    background_tasks: BackgroundTasks, 
    nombre_evento: str, 
    titulo: str, 
    cuerpo: str, 
    ruta_destino: str = None
):
    """
    Despachador universal. 
    Busca usuarios y distribuye de forma asíncrona tanto por Web Push como por Email (vía Brevo)
    respetando de forma estricta las preferencias del alumno en la base de datos.
    """
    try:
        # 1. Buscamos el evento en el catálogo para obtener su idtipo
        evento = db.query(NotificacionTipo).filter(NotificacionTipo.nombre_clave == nombre_evento).first()
        if not evento:
            logger.error(f"[Despachador] El evento '{nombre_evento}' no existe en el catálogo.")
            return

        # ==========================================
        # CANAL A: GESTIÓN DE WEB PUSH (Opt-out)
        # ==========================================
        # Por defecto es True, buscamos quién lo ha desactivado explícitamente
        usuarios_bloqueados_push = db.query(UsuarioNotificacionConfig.idusuario).filter(
            UsuarioNotificacionConfig.idtipo == evento.idtipo,
            UsuarioNotificacionConfig.canal_push == False
        ).all()
        set_bloqueados_push = {u.idusuario for u in usuarios_bloqueados_push}

        todas_las_suscripciones = db.query(SuscripcionPush).all()
        push_enviados = 0

        for sub in todas_las_suscripciones:
            if sub.idusuario in set_bloqueados_push:
                continue

            background_tasks.add_task(
                enviar_notificacion_push,
                suscripcion_db=sub,
                titulo=titulo,
                cuerpo=cuerpo,
                ruta_destino=ruta_destino,
                db=db
            )
            push_enviados += 1

        # ==========================================
        # CANAL B: GESTIÓN DE EMAILS (Opt-in)
        # ==========================================
        # Por defecto es False, buscamos quién lo ha activado explícitamente
        usuarios_activos_email = db.query(UsuarioNotificacionConfig.idusuario).filter(
            UsuarioNotificacionConfig.idtipo == evento.idtipo,
            UsuarioNotificacionConfig.canal_email == True
        ).all()
        lista_ids_email = [u.idusuario for u in usuarios_activos_email]

        email_enviados = 0
        if lista_ids_email:
            # Traemos los correos electrónicos correspondientes de la tabla Usuario
            alumnos_a_notificar = db.query(Usuario).filter(
                Usuario.idusuario.in_(lista_ids_email),
                Usuario.activo >= 1 # Seguridad básica: solo alumnos activos
            ).all()

            for alumno in alumnos_a_notificar:
                if alumno.email:
                    background_tasks.add_task(
                        enviar_correo_notificacion_evento,
                        email_destino=alumno.email,
                        titulo=titulo,
                        cuerpo=cuerpo,
                        ruta_destino=ruta_destino
                    )
                    email_enviados += 1

        logger.info(
            f"[Despachador] Procesado evento '{nombre_evento}'. "
            f"Encolados: {push_enviados} Web Push y {email_enviados} Correos electrónicos."
        )
        
    except Exception as e:
        logger.error(f"[Despachador] Error crítico distribuyendo el evento {nombre_evento}: {e}")