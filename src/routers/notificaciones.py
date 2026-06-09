import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.utils.db_tools import get_write_db
from src.utils.auth import usuario_obligatorio  # Tu autenticación por cookies
from src.models.notificaciones import NotificacionTipo, UsuarioNotificacionConfig
from src.schemas.notificaciones import PreferenciaNotificacionSchema, ActualizarPreferenciaSchema

logger = logging.getLogger("aamm")

router = APIRouter(
    prefix="/api/notificaciones",
    tags=["Preferencias de Notificaciones"]
)

@router.get("/preferencias", response_model=List[PreferenciaNotificacionSchema])
def obtener_preferencias_usuario(
    db: Session = Depends(get_write_db),
    current_user = Depends(usuario_obligatorio)
):
    """
    Devuelve el catálogo de notificaciones con el estado actual del alumno.
    Si no tiene registro guardado, se devuelve True (activado) por defecto.
    """
    # 1. Traemos todo el catálogo disponible
    tipos_eventos = db.query(NotificacionTipo).all()
    
    # 2. Traemos las configuraciones guardadas por este usuario específico
    config_usuario = db.query(UsuarioNotificacionConfig).filter(
        UsuarioNotificacionConfig.idusuario == current_user.idusuario
    ).all()
    
    # Mapeamos las configuraciones en un diccionario indexado por idtipo para buscar rápido
    mapa_config = {c.idtipo: c for c in config_usuario}
    
    resultado = []
    for tipo in tipos_eventos:
        # Si el usuario ya personalizó este tipo, usamos su valor. Si no, por defecto es True en push
        has_config = mapa_config.get(tipo.idtipo)
        
        resultado.append({
            "nombre_clave": tipo.nombre_clave,
            "nombre_pantalla": tipo.nombre_pantalla,
            "descripcion": tipo.descripcion,
            "canal_push": has_config.canal_push if has_config else True, # 🌟 Por defecto True
            "canal_email": has_config.canal_email if has_config else False # 🌟 Por defecto False
        })
        
    return resultado


@router.post("/preferencias/guardar")
def actualizar_preferencia_usuario(
    datos: ActualizarPreferenciaSchema,
    db: Session = Depends(get_write_db),
    current_user = Depends(usuario_obligatorio)
):
    """
    Modifica o crea la preferencia de un usuario para un canal concreto.
    """
    # 1. Validamos que el tipo de evento exista en el catálogo
    tipo = db.query(NotificacionTipo).filter(NotificacionTipo.nombre_clave == datos.nombre_clave).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="El tipo de evento no existe.")
        
    if datos.canal not in ["push", "email"]:
        raise HTTPException(status_code=400, detail="Canal no válido. Use 'push' o 'email'.")

    # 2. Buscamos si ya existe la fila de configuración para este usuario y tipo
    config = db.query(UsuarioNotificacionConfig).filter(
        UsuarioNotificacionConfig.idusuario == current_user.idusuario,
        UsuarioNotificacionConfig.idtipo == tipo.idtipo
    ).first()

    # 3. Si no existe, creamos el registro inicial (Upsert manual)
    if not config:
        config = UsuarioNotificacionConfig(
            idusuario=current_user.idusuario,
            idtipo=tipo.idtipo,
            canal_push=True,  # Valores por defecto base
            canal_email=False
        )
        db.add(config)

    # 4. Aplicamos el cambio dinámicamente según el canal modificado
    if datos.canal == "push":
        config.canal_push = datos.valor
    elif datos.canal == "email":
        config.canal_email = datos.valor

    try:
        db.commit()
        logger.info(f"Preferencia '{datos.nombre_clave}' ({datos.canal}) actualizada a {datos.valor} para el usuario {current_user.idusuario}")
        return {"status": "ok", "message": "Preferencia guardada correctamente."}
    except Exception as e:
        db.rollback()
        logger.error(f"Error al guardar la preferencia en MySQL: {e}")
        raise HTTPException(status_code=500, detail="No se pudo procesar la solicitud.")



# prueba de notificaciones push (simulación de evento) - para desarrollo, no es un endpoint real de producción
"""
from fastapi import BackgroundTasks 

@router.post("/simular-video")
def simular_subida_de_video(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_write_db),
    current_user = Depends(usuario_obligatorio) # Solo profes o tú logueado
):
    #Simula que un profesor sube un vídeo. Dispara el despachador para 
    #notificar a todos los alumnos que tengan el check activo.
    
    from src.services.notificaciones import despachar_notificacion_evento

    # Llamamos al despachador
    despachar_notificacion_evento(
        db=db,
        background_tasks=background_tasks,
        nombre_evento="nuevo_video",
        titulo="🥋 ¡Nueva lección disponible!",
        cuerpo="Se ha subido el videotutorial: 'Defensa personal y fluidez de cadera'.",
        ruta_destino="/videos/leccion-1"
    )

    return {"status": "ok", "message": "Simulación lanzada en segundo plano."}
"""