import logging
from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles

from src.utils.logging_config import configurar_logs, client_ip_ctx  # Importamos el módulo de logs
from src.utils import auth
from src.utils.db_tools import engine_read_only, engine_write, get_read_db
from src.models import models

# Creamos las tablas si no existen (aunque ya las tengas, esto asegura sincronización)
models.Base.metadata.create_all(bind=engine_read_only)


###########################################################
# Inicializamos la aplicación FastAPI
app = FastAPI(title="AAMM - Artes Marciales")


###########################################################
# Configuramos el manejo de archivos estáticos (CSS, JS y vídeos)
app.mount("/static", StaticFiles(directory="src/static"), name="static")


###########################################################
# Configurar el sistema de logs global
from src.config import LOG_LEVEL

configurar_logs(LOG_LEVEL)
logger = logging.getLogger("AAMM-APP")

logger.info('Iniciando la aplicación web de Artes Marciales')   

# 2. El Middleware se queda aquí porque necesita interactuar con la 'app'
class LogIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Capturamos la IP real (Cloudflare -> Docker)
        ip_real = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
        if not ip_real and request.client:
            ip_real = request.client.host
        else:
            ip_real = ip_real.split(",")[0].strip() if ip_real else "IP desconocida"
            
        # Seteamos la IP en el contexto antes de procesar la petición
        token = client_ip_ctx.set(ip_real)
        try:
            response = await call_next(request)
            return response
        finally:
            client_ip_ctx.reset(token)

app.add_middleware(LogIPMiddleware)




###########################################################
# Cargamos los routers
from src.routers import login
app.include_router(login.router)

from src.routers import login
app.include_router(login.router_raiz)

from src.routers import usuarios
app.include_router(usuarios.router)

from src.routers import frontEnd
app.include_router(frontEnd.router)

from src.routers import tecnicas
app.include_router(tecnicas.router)

from src.routers import videos
app.include_router(videos.router)

# Si entra en una ruta no definida, redirige a la raíz
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, __):
    logger.warning(f"Ruta no encontrada: {request.url.path}, redirigiendo a la raíz")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    import uvicorn
    # Cambiado a 0.0.0.0 para que escuche fuera del contenedor si lo corres directo
    uvicorn.run("src.main:app", host="0.0.0.0", port=8888, reload=True)