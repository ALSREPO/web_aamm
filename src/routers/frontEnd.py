import logging

from src.utils.auth import obtener_usuario_actual
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from src.models.models import Usuario
from src.config import ORDEN_LISTADO_TECNICAS, SENTIDO_ORDEN_LISTADO_TECNICAS, NUMERO_TECNICAS_POR_PAGINA

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
        "ORDEN_LISTADO_TECNICAS" : ORDEN_LISTADO_TECNICAS,
        "NUMERO_TECNICAS_POR_PAGINA" : NUMERO_TECNICAS_POR_PAGINA,
        "SENTIDO_ORDEN_LISTADO_TECNICAS" : SENTIDO_ORDEN_LISTADO_TECNICAS,
    })


########################
# /login, /registro y /logout

@router.get("/login")
def vista_login(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    # Si ya está logueado y trata de ir al login, lo mandamos a la home
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("usuarios/login.html", {"request": request})

@router.get("/registro")
def vista_registro(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    # Si ya está logueado, no tiene sentido que se registre, lo mandamos a la home
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("usuarios/registro.html", {"request": request})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    # Borramos la cookie de acceso 
    response.delete_cookie("access_token") 
    return response

########################
# Páginas de usuarios
# /perfil
# /admin/gestion-usuarios

@router.get("/perfil", response_class=HTMLResponse)
async def pagina_perfil(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("usuarios/perfil.html", {"request": request, "user": user})


@router.get("/admin/gestion-usuarios", response_class=HTMLResponse)
async def pagina_admin_gestion_usuarios(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 2:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("usuarios/admin_gestion_usuarios.html", {"request": request, "user": user})
