import logging

from src.utils.auth import obtener_usuario_actual
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from src.models.models import Usuario

router = APIRouter(prefix="", tags=["FrontEnd"])

###########################################################
# --- Configuración de Archivos Estáticos y Plantillas ---

templates = Jinja2Templates(directory="src/templates")

logger = logging.getLogger("AAMM-APP-FrontEnd")


# --- Rutas de Frontend (Jinja2) ---

########################
# / - Página Principal (Index)

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


########################
# /login y /registro

@router.get("/login")
def vista_login(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    # Si ya está logueado y trata de ir al login, lo mandamos a la home
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/registro")
def vista_registro(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    # Si ya está logueado, no tiene sentido que se registre, lo mandamos a la home
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("registro.html", {"request": request})


########################
# /perfil

@router.get("/perfil", response_class=HTMLResponse)
async def pagina_perfil(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("usuarios/perfil.html", {"request": request, "user": user})