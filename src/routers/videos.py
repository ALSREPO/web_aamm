import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Header
from fastapi.responses import FileResponse
import os
from shutil import copyfileobj
from sqlalchemy.orm import Session

from src.models.models import Usuario, Video
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_admin, usuario_obligatorio
from src.config import RUTA_VIDEOS, TAMANYO_MAXIMO_SUBIDA_VIDEOS


router = APIRouter(prefix="/api/videos", tags=["Videos"])

logger = logging.getLogger("AAMM-APP-videos")


@router.post("/subir-video", dependencies=[Depends(verificar_admin)])
async def subir_video(file: UploadFile = File(...), admin: Usuario = Depends(usuario_obligatorio)):
    
    try:
        # Validar extensión del archivo
        if not file.filename.lower().endswith(('.mp4', '.mov', '.avi')):
            logger.warning(f"Intento de subir archivo con formato no permitido '{file.filename}' por admin ID_ADMIN[{admin.idusuario}]")
            raise HTTPException(status_code=400, detail="Solo se permiten archivos .mp4")
        
        # Validar tamaño del archivo (ejemplo: máximo 100MB)
        contents = await file.read()
        if len(contents) > TAMANYO_MAXIMO_SUBIDA_VIDEOS * 1024 * 1024:
            logger.warning(f"Intento de subir archivo demasiado grande '{file.filename}' ({len(contents) / (1024 * 1024):.2f} MB) por admin ID_ADMIN[{admin.idusuario}]")
            raise HTTPException(status_code=400, detail=f"Archivo demasiado grande. Máximo {TAMANYO_MAXIMO_SUBIDA_VIDEOS}MB.")
        
        # Resetear el cursor del archivo para que se pueda leer de nuevo
        await file.seek(0)
    except Exception as e:
        logger.error(f"Error al validar archivo '{file.filename}' por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar el archivo")
    
    try:
        os.makedirs(RUTA_VIDEOS, exist_ok=True)
    except Exception as e:
        logger.error(f"Error al crear directorio de videos '{RUTA_VIDEOS}' por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al preparar el almacenamiento del video")

    try:
         # Definimos la ruta de destino 
        ruta_destino = os.path.join(RUTA_VIDEOS, file.filename)
        
        # Guardar el archivo en el servidor
        with open(ruta_destino, "wb") as buffer:
            copyfileobj(file.file, buffer)
        
        logger.info(f"Archivo '{file.filename}' subido exitosamente, tamaño {len(contents) / (1024 * 1024):.2f} MB, por admin ID_ADMIN[{admin.idusuario}]")
        return {"filename": file.filename}
    except Exception as e:
        logger.error(f"Error al guardar archivo '{file.filename}' por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el archivo")



@router.get("/archivos-videos", dependencies=[Depends(verificar_admin)])
def listar_archivos_videos(admin: Usuario = Depends(usuario_obligatorio)):
    
    if not os.path.exists(RUTA_VIDEOS):
        # Esto te dirá exactamente qué ruta está intentando buscar Python
        raise HTTPException(status_code=500, detail=f"Ruta no encontrada: {RUTA_VIDEOS}")
        
    ficheros = [f for f in os.listdir(RUTA_VIDEOS) if f.endswith(('.mp4', '.mov', '.avi'))]
    logger.info(f"Listado de archivos de videos obtenido por admin ID_ADMIN[{admin.idusuario}]. Total archivos: {len(ficheros)}")
    return sorted(ficheros)


@router.delete("/eliminar-archivo-fisico", dependencies=[Depends(verificar_admin)])
def eliminar_archivo_fisico(filename: str, admin: Usuario = Depends(usuario_obligatorio)):
    try:
        # Esto te dirá exactamente qué ruta está intentando eliminar Python
        ruta_completa = os.path.join(RUTA_VIDEOS, filename)
        if not os.path.exists(ruta_completa):
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {ruta_completa}")
    except Exception as e:
        logger.error(f"Error al verificar existencia del archivo '{filename}' por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al verificar el archivo")
        
    # Seguridad: Evitar que intenten borrar archivos fuera de la carpeta de vídeos
    if not os.path.abspath(ruta_completa).startswith(os.path.abspath(RUTA_VIDEOS)):
        logger.warning(f"Intento de eliminar archivo fuera de la carpeta de videos: '{filename}' por admin ID_ADMIN[{admin.idusuario}]")
        raise HTTPException(status_code=400, detail="Ruta no permitida")
            
    if os.path.exists(ruta_completa):
        os.remove(ruta_completa)
        logger.info(f"Archivo eliminado: {ruta_completa}, por admin ID_ADMIN[{admin.idusuario}]")
        return {"detail": "Archivo eliminado"}
    
    logger.warning(f"Intento de eliminar archivo no encontrado: '{filename}' por admin ID_ADMIN[{admin.idusuario}]")
    raise HTTPException(status_code=404, detail="Archivo no encontrado")


@router.get("/auditoria-videos", dependencies=[Depends(verificar_admin)])
def auditoria_videos(db: Session = Depends(get_read_db), admin: Usuario = Depends(usuario_obligatorio)):
    # 1. Vídeos en el DISCO
    archivos_fisicos = set([f for f in os.listdir(RUTA_VIDEOS) if f.endswith(('.mp4', '.mov', '.avi'))])

    # 2. Vídeos en la BASE DE DATOS
    videos_db = db.query(Video.video).all()
    nombres_db = set([v[0] for v in videos_db])

    # 3. Encontrar huérfanos (Están en disco pero NO en DB)
    huerfanos = sorted(list(archivos_fisicos - nombres_db))
    
    logger.info(f"Auditoría de videos completada por admin ID_ADMIN[{admin.idusuario}]. Total huérfanos: {len(huerfanos)}")

    return {
        "huerfanos": huerfanos,
        "total_fisicos": len(archivos_fisicos),
        "total_en_uso": len(nombres_db)
    }




@router.get("/{nombre_video}", dependencies=[Depends(usuario_obligatorio)])
async def obtener_video_protegido(
    nombre_video: str,
    # Capturamos la cabecera Sec-Fetch-Mode que envía el navegador de forma automática
    sec_fetch_mode: str = Header(None, alias="Sec-Fetch-Mode"),
    user: Usuario = Depends(usuario_obligatorio)
):
    # Si el modo es 'navigate', es que han metido la URL a mano en la barra de direcciones
    if sec_fetch_mode == "navigate":
        logger.warning(f"Intento de acceso directo al video '{nombre_video}' con Sec-Fetch-Mode 'navigate', por usuario ID_USUARIO[{user.idusuario}]")
        raise HTTPException(
            status_code=403, 
            detail="Acceso no permitido."
        )
    
    # Evitamos ataques de salto de directorio (ej: ../../etc/passwd)
    if ".." in nombre_video or nombre_video.startswith("/"):
        raise HTTPException(status_code=400, detail="Ruta no permitida")
        
    ruta_completa = os.path.join(RUTA_VIDEOS, nombre_video)
    
    if not os.path.exists(ruta_completa):
        logger.warning(f"Vídeo no encontrado: '{nombre_video}' por usuario ID_USUARIO[{user.idusuario}]")
        raise HTTPException(status_code=404, detail="El vídeo no existe")
        
    # FileResponse en FastAPI maneja automáticamente los rangos de bytes (206 Partial Content)
    # permitiendo pausar, rebobinar y avanzar el vídeo nativamente en el navegador.
    return FileResponse(ruta_completa, media_type="video/mp4")