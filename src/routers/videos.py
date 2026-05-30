import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
from shutil import copyfileobj

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
            logger.warning(f"Intento de subir archivo con formato no permitido '{file.filename}' por admin {admin.idusuario} - {admin.email}")
            raise HTTPException(status_code=400, detail="Solo se permiten archivos .mp4")
        
        # Validar tamaño del archivo (ejemplo: máximo 100MB)
        contents = await file.read()
        if len(contents) > TAMANYO_MAXIMO_SUBIDA_VIDEOS * 1024 * 1024:
            logger.warning(f"Intento de subir archivo demasiado grande '{file.filename}' ({len(contents) / (1024 * 1024):.2f} MB) por admin {admin.idusuario} - {admin.email}")
            raise HTTPException(status_code=400, detail=f"Archivo demasiado grande. Máximo {TAMANYO_MAXIMO_SUBIDA_VIDEOS}MB.")
        
        # Resetear el cursor del archivo para que se pueda leer de nuevo
        await file.seek(0)
    except Exception as e:
        logger.error(f"Error al validar archivo '{file.filename}' por admin {admin.idusuario} - {admin.email}: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar el archivo")
    
    try:
        os.makedirs(RUTA_VIDEOS, exist_ok=True)
    except Exception as e:
        logger.error(f"Error al crear directorio de videos '{RUTA_VIDEOS}' por admin {admin.idusuario} - {admin.email}: {e}")
        raise HTTPException(status_code=500, detail="Error al preparar el almacenamiento del video")

    try:
         # Definimos la ruta de destino 
        ruta_destino = os.path.join(RUTA_VIDEOS, file.filename)
        
        # Guardar el archivo en el servidor
        with open(ruta_destino, "wb") as buffer:
            copyfileobj(file.file, buffer)
        
        logger.info(f"Archivo '{file.filename}' subido exitosamente, tamaño {len(contents) / (1024 * 1024):.2f} MB, por admin {admin.idusuario} - {admin.email}")
        return {"filename": file.filename}
    except Exception as e:
        logger.error(f"Error al guardar archivo '{file.filename}' por admin {admin.idusuario} - {admin.email}: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el archivo")



@router.get("/archivos-videos", dependencies=[Depends(verificar_admin)])
def listar_archivos_videos(admin: Usuario = Depends(usuario_obligatorio)):
    
    if not os.path.exists(RUTA_VIDEOS):
        # Esto te dirá exactamente qué ruta está intentando buscar Python
        raise HTTPException(status_code=500, detail=f"Ruta no encontrada: {RUTA_VIDEOS}")
        
    ficheros = [f for f in os.listdir(RUTA_VIDEOS) if f.endswith(('.mp4', '.mov', '.avi'))]
    logger.info(f"Listado de archivos de videos obtenido por admin {admin.idusuario} - {admin.email}. Total archivos: {len(ficheros)}")
    return sorted(ficheros)