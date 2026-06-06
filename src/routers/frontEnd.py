import logging

import os
from src.utils.auth import obtener_usuario_actual
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from src.models.models import Usuario
from src.models.horarios import HorarioClase # Importa tu nuevo modelo
from sqlalchemy import asc
from src.config import NUMERO_TECNICAS_POR_PAGINA, LOG_FILE_PATH, MOSTRAR_HORARIO

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
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "NUMERO_TECNICAS_POR_PAGINA" : NUMERO_TECNICAS_POR_PAGINA,
        "MOSTRAR_HORARIO" : MOSTRAR_HORARIO,
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
    if not user or user.activo < 1:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("usuarios/perfil.html", {"request": request, "user": user, "MOSTRAR_HORARIO" : MOSTRAR_HORARIO,})


@router.get("/admin/gestion-usuarios", response_class=HTMLResponse)
async def pagina_admin_gestion_usuarios(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 2:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("usuarios/admin_gestion_usuarios.html", {"request": request, "user": user, "MOSTRAR_HORARIO" : MOSTRAR_HORARIO,})


########################
# detalle de una técnica

@router.get("/tecnica/{idtecnica}", response_class=HTMLResponse)
async def pagina_detalle_tecnica(
    request: Request, 
    idtecnica: int, 
    user: Usuario = Depends(obtener_usuario_actual)
):
    if not user or user.activo < 1:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse("tecnicas/detalle_tecnica.html", {
        "request": request, 
        "idtecnica": idtecnica, 
        "user": user  # Lo pasamos para que el HTML sepa si es admin o no
        ,"MOSTRAR_HORARIO" : MOSTRAR_HORARIO,
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
        ,"MOSTRAR_HORARIO" : MOSTRAR_HORARIO,
    })

########################
# Crear y Editar las Disciplinas y Etiquetas

@router.get("/admin/tablas-bbdd", response_class=HTMLResponse)
async def pagina_admin_tablas(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 2:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("tecnicas/admin_tablas_bbdd.html", {"request": request, "user": user, "MOSTRAR_HORARIO" : MOSTRAR_HORARIO,})


########################
# Página "Acerca de"
@router.get("/acerca-de", response_class=HTMLResponse)
def pagina_acerca_de(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    return templates.TemplateResponse("acerca_de.html", {"request": request, "user": user, "MOSTRAR_HORARIO" : MOSTRAR_HORARIO,})


########################
# Favicon (icono de la pestaña del navegador)
@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Ojo: como FastAPI ejecuta la app desde la raíz del proyecto, 
    # la ruta relativa sigue siendo la misma desde donde se levanta el proceso.
    ruta_favicon = os.path.join("src", "static", "favicon.ico")
    
    if os.path.exists(ruta_favicon):
        return FileResponse(ruta_favicon)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

########################
# Página de visualización de logs (solo para admins)
@router.get("/admin/logs", response_class=HTMLResponse)
def pagina_logs(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 2:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("logs/admin_logs.html", {"request": request, "user": user, "LOG_FILE_PATH": LOG_FILE_PATH.split("/")[-1], "MOSTRAR_HORARIO" : MOSTRAR_HORARIO,})



########################
# HORARIO DE CLASES: Vista del Horario (Pública para alumnos logueados)

@router.get("/horarios", response_class=HTMLResponse)
async def pagina_ver_horario(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    print(f"MOSTRAR_HORARIO: {MOSTRAR_HORARIO}")  # Debug para verificar el valor de MOSTRAR_HORARIO
    # Si el "portero" no devuelve un usuario, al login directo
    if not user or user.activo < 1 or MOSTRAR_HORARIO == 0:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # 1. Traemos la sesión de lectura directamente desde el request state
        # (O usa Depends(get_read_db) si prefieres inyectarlo en la función)
        db = request.state.db if hasattr(request.state, "db") else None
        if not db:
            from src.utils.db_tools import get_read_db
            db = next(get_read_db())

        # 2. Consultamos todas las clases ordenadas por hora de inicio
        clases = db.query(HorarioClase).order_by(asc(HorarioClase.hora_inicio)).all()

        # 3. Construimos el casillero de Lunes (1) a Viernes (5) para agruparlas
        horario_agrupado = {i: [] for i in range(1, 6)}
        for clase in clases:
            if clase.dia_semana in horario_agrupado:
                horario_agrupado[clase.dia_semana].append(clase)

        logger.info(f"Usuario ID_USUARIO[{user.idusuario}] visualizando el horario dinámico")
        
        return templates.TemplateResponse("horarios/horario.html", {
            "request": request,
            "user": user,
            "horario": horario_agrupado,
            "MOSTRAR_HORARIO" : MOSTRAR_HORARIO,
        })

    except Exception as e:
        logger.error(f"Error al renderizar la página de horarios para usuario {user.idusuario}: {e}")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


########################
# HORARIO DE CLASES: Panel de Gestión del Horario (Solo para Administradores)

@router.get("/admin/horarios", response_class=HTMLResponse)
async def pagina_admin_gestion_horarios(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    # Protección estricta de nivel de acceso (activo < 2 no pasa)
    if not user or user.activo < 2:
        logger.warning(f"Intento de acceso no autorizado a gestión de horarios por ID_USUARIO[{user.idusuario if user else 'Anónimo'}]")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    try:
        db = request.state.db if hasattr(request.state, "db") else None
        if not db:
            from src.utils.db_tools import get_read_db
            db = next(get_read_db())

        # Hacemos exactamente la misma agrupación para mostrarle lo que hay publicado
        clases = db.query(HorarioClase).order_by(asc(HorarioClase.hora_inicio)).all()
        
        horario_agrupado = {i: [] for i in range(1, 6)}
        for clase in clases:
            if clase.dia_semana in horario_agrupado:
                horario_agrupado[clase.dia_semana].append(clase)

        logger.info(f"Admin ID_ADMIN[{user.idusuario}] entrando al panel de control del horario")

        return templates.TemplateResponse("horarios/admin_editar_horario.html", {
            "request": request,
            "user": user,
            "horario": horario_agrupado,
            "MOSTRAR_HORARIO" : MOSTRAR_HORARIO,
        })

    except Exception as e:
        logger.error(f"Error al renderizar el panel de administración de horarios: {e}")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)