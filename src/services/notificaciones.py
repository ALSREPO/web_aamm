# centralizará el envío de cualquier notificación futura

import logging
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from src.models.notificaciones import NotificacionTipo, UsuarioNotificacionConfig
from src.models.push import SuscripcionPush
from src.utils.push_notifications import enviar_notificacion_push

logger = logging.getLogger("aamm")

def despachar_notificacion_evento(
    db: Session, 
    background_tasks: BackgroundTasks, 
    nombre_evento: str, 
    titulo: str, 
    cuerpo: str, 
    ruta_destino: str = None
):
    """
    Despachador universal. Busca usuarios suscritos al 'nombre_evento'
    y encola el envío Web Push en las tareas de segundo plano de FastAPI.
    """
    try:
        # 1. Buscamos el evento en el catálogo para obtener su idtipo
        evento = db.query(NotificacionTipo).filter(NotificacionTipo.nombre_clave == nombre_evento).first()
        if not evento:
            logger.error(f"[Despachador] El evento '{nombre_evento}' no existe en el catálogo.")
            return

        # 2. Buscamos qué usuarios NO quieren recibir este push (tienen canal_push = False)
        # Recordamos: Por defecto todo el mundo está suscrito (True), así que buscamos los "opt-out"
        usuarios_bloqueados = db.query(UsuarioNotificacionConfig.idusuario).filter(
            UsuarioNotificacionConfig.idtipo == evento.idtipo,
            UsuarioNotificacionConfig.canal_push == False
        ).all()
        
        # Convertimos a un set de Python para buscar a velocidad luz O(1)
        set_bloqueados = {u.idusuario for u in usuarios_bloqueados}

        # 3. Traemos todas las suscripciones de navegadores activas en la escuela
        todas_las_suscripciones = db.query(SuscripcionPush).all()

        enviados = 0
        for sub in todas_las_suscripciones:
            # Si el dueño del dispositivo ha desactivado este tipo de notificación, lo saltamos 🛑
            if sub.idusuario in set_bloqueados:
                continue

            # 4. Encolamos el envío real en segundo plano 🚀
            # Esto evita que el endpoint actual tarde segundos de más en responder al usuario
            background_tasks.add_task(
                enviar_notificacion_push,
                suscripcion_db=sub,
                titulo=titulo,
                cuerpo=cuerpo,
                ruta_destino=ruta_destino
            )
            enviados += 1

        logger.info(f"[Despachador] Encoladas {enviados} notificaciones push para el evento '{nombre_evento}'.")

    except Exception as e:
        logger.error(f"[Despachador] Error crítico distribuyendo el evento {nombre_evento}: {e}")