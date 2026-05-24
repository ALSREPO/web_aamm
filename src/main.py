import logging
from fastapi import FastAPI

from src.utils.db_tools import engine_read_only, engine_write, get_read_db
from src.models import models
from src.routers import usuarios

# Creamos las tablas si no existen (aunque ya las tengas, esto asegura sincronización)
models.Base.metadata.create_all(bind=engine_read_only)

###########################################################
# Importamos la configuración del LOG_LEVEL
from src.config import LOG_LEVEL

# Configurar el sistema de logs global
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AAMM-APP")

logger.info('Iniciando la aplicación web de Artes Marciales')


###########################################################
# Inicializamos la aplicación FastAPI
app = FastAPI(title="AAMM - Artes Marciales")


app.include_router(usuarios.router)


if __name__ == "__main__":
    import uvicorn
    # Cambiado a 0.0.0.0 para que escuche fuera del contenedor si lo corres directo
    uvicorn.run("src.main:app", host="0.0.0.0", port=8888, reload=True)