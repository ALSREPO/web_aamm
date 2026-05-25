import logging

from src.utils.auth import obtener_usuario_actual
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.models.models import Usuario


router = APIRouter(prefix="", tags=["FrontEnd"])

###########################################################
# --- Configuración de Archivos Estáticos y Plantillas ---

templates = Jinja2Templates(directory="src/templates")

logger = logging.getLogger("AAMM-APP-FrontEnd")


# --- Rutas de Frontend (Jinja2) ---

@router.get("/")
def home(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    # Si el "portero" no devuelve un usuario, redirigimos al login
    if not user:
        logger.debug(f"No hay usuario autenticado, redirigiendo a /login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Si está logueado, cargamos el listado (index.html)
    logger.debug(f"Usuario autenticado: {user.email}, mostrando página principal")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
    })