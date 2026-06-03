import logging

from src.utils.auth import obtener_usuario_actual
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from src.models.models import Usuario
from src.config import NUMERO_TECNICAS_POR_PAGINA

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
    logger.debug(f"Usuario autenticado, mostrando página principal, ID_USUARIO[{user.idusuario}]")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "NUMERO_TECNICAS_POR_PAGINA" : NUMERO_TECNICAS_POR_PAGINA,
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


########################
# detalle de una técnica

@router.get("/tecnica/{idtecnica}", response_class=HTMLResponse)
async def pagina_detalle_tecnica(
    request: Request, 
    idtecnica: int, 
    user: Usuario = Depends(obtener_usuario_actual)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse("tecnicas/detalle_tecnica.html", {
        "request": request, 
        "idtecnica": idtecnica, 
        "user": user  # Lo pasamos para que el HTML sepa si es admin o no
    })


########################
# Crear y Editar una técnica

@router.get("/admin/tecnica", response_class=HTMLResponse)
async def pagina_admin_tecnica(
    request: Request, 
    idtecnica: Optional[int] = None, # Añadimos el ID opcional. Si lo incluye, se edita esa tecnica. Si no lo incluye, se crea una nueva tecnica
    user: Usuario = Depends(obtener_usuario_actual)
):
    if not user or user.activo < 2:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("tecnicas/crear_editar_tecnica.html", {
        "request": request, 
        "user": user, 
        "idtecnica": idtecnica # Lo pasamos a la plantilla
    })

########################
# Crear y Editar las Disciplinas y Etiquetas

@router.get("/admin/tablas-bbdd", response_class=HTMLResponse)
async def pagina_admin_tablas(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 2:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("tecnicas/admin_tablas_bbdd.html", {"request": request, "user": user})


########################
# Página "Acerca de"
@router.get("/acerca-de", response_class=HTMLResponse)
def pagina_acerca_de(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    return templates.TemplateResponse("acerca_de.html", {"request": request, "user": user})


########################
# Página de visualización de logs (solo para admins)
@router.get("/logs", response_class=HTMLResponse)
def pagina_logs(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 2:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("logs/admin_logs.html", {"request": request, "user": user})
