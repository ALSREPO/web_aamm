import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta, timezone
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_password, crear_token_acceso, crear_token_verificacion, verificar_token_verificacion, obtener_password_hash, enviar_correo_verificacion, verificar_admin, usuario_obligatorio
from src.utils.telegram import enviar_solicitud_registro_telegram
from src.models.models import Usuario
from src.schemas.autenticacion import UsuarioLogin, UsuarioCreate, Mensaje
from src.config import ACCESS_TOKEN_COOKIE_MAX_AGE

# 1. El router para tus rutas normales
router = APIRouter(
    prefix="/api/autenticacion",
    tags=["autenticación"]
)

# 2. El router específico para rutas que van en la raíz
router_raiz = APIRouter(
    tags=["autenticación"] # Mantenemos el tag para que en el Swagger salgan juntos
)
import logging
logger = logging.getLogger("AAMM-APP-login")


# /login 
# /logout
# /registro
# /usuarios/{idusuario}/activar

import os
from datetime import datetime, timedelta, timezone

@router.post("/login")
def login(response: Response, usuario: UsuarioLogin, db: Session = Depends(get_read_db)):
    # 1. Buscar usuario
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    
    # 2. Validar existencia y contraseña
    if not db_user or not verificar_password(usuario.password, db_user.password):
        logger.warning(f"Intento de login fallido para: ID_USUARIO[{db_user.idusuario if db_user else 'N/A'}]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos."
        )
    
    # 3. Validar si el Email está Verificado ---
    if not db_user.email_verificado:
        logger.warning(f"Intento de login con email no verificado para ID_USUARIO[{db_user.idusuario}]")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes verificar tu correo electrónico antes de acceder. Revisa tu bandeja de entrada."
        )
    
    # 4. Verificar si está activo
    if db_user.activo == 0:
        logger.warning(f"Intento de login con cuenta inactiva para ID_USUARIO[{db_user.idusuario}]")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está verificada, pero un administrador debe activarla manualmente."
        )
    
    # Configuramos la expiración de la cookie y del JWT usando el mismo valor del fichero de configuración.
    # CALCULOS DE TIEMPO (Colocados aquí dentro para que se ejecuten en cada login real)
    max_age_segundos = int(os.getenv("ACCESS_TOKEN_COOKIE_MAX_AGE", 2678400)) 
    fecha_final = datetime.now(timezone.utc) + timedelta(seconds=max_age_segundos)

    # 5. Crear el Token (Le pasamos 'fecha_final' a nuestro nuevo parámetro 'expires_at')
    access_token = crear_token_acceso(data={"sub": db_user.email}, expires_at=fecha_final)
    
    # 6. CREAR LA COOKIE
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,   # No accesible desde JS
        max_age=max_age_segundos,
        expires=fecha_final, 
        samesite="lax",  # Protección CSRF básica
        secure=False     # Cambiar a True cuando tengas HTTPS/SSL
    )

    logger.info(f"Inicio de sesión para ID_USUARIO[{db_user.idusuario}]")
    
    return {"message": "Login exitoso", "redirect": "/"}


@router.post("/logout")
def logout(response: Response):
    """Elimina la cookie de sesión"""
    response.delete_cookie("access_token")
    return {"message": "Sesión cerrada"}


@router.post("/registro", response_model=Mensaje)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_write_db)):
    # 1. Verificar si el email existe
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    
    if db_user:
        # Si ya está verificado, no permitimos hacer nada más
        if db_user.email_verificado:
            logger.info(f"Intento de registro con email ya verificado: ID_USUARIO[{db_user.idusuario}]")
            raise HTTPException(status_code=400, detail="El email ya está registrado y verificado")
        
        # Si NO está verificado, actualizamos sus datos (por si cambió el nombre o pass)
        db_user.nombre = usuario.nombre
        db_user.password = obtener_password_hash(usuario.password)
        db_user.fechaCreacion = date.today()
        # No hace falta db.add, SQLAlchemy detecta el cambio
        logger.debug(f"Usuario actualizado: ID_USUARIO[{db_user.idusuario}]")
    else:
        # Caso normal: Usuario nuevo
        db_user = Usuario(
            nombre=usuario.nombre,
            email=usuario.email,
            password=obtener_password_hash(usuario.password),
            fechaCreacion=date.today(),
            activo=0,
            email_verificado=False
        )
        db.add(db_user)
        logger.info(f"Nuevo usuario registrado, pendiente de validación y de activación: ID_USUARIO[{db_user.idusuario}]")

    db.commit()
    
    # 2. Generar y enviar nuevo correo (esto sirve tanto para nuevos como para re-intentos)
    token = crear_token_verificacion(db_user.email)
    envio_ok = enviar_correo_verificacion(db_user.email, token)

    if not envio_ok:
        # Opcional: podrías decidir si borrar el usuario o avisar de un error
        logger.error(f"Aviso: El correo para verificar la cuenta de ID_USUARIO[{db_user.idusuario}] no se pudo enviar")

    return {"message": "Si los datos son correctos, recibirás un correo para verificar tu cuenta."}



@router_raiz.get("/verificar_mail", response_class=HTMLResponse)
def verificar_mail(token: str = Query(...), db: Session = Depends(get_write_db)):
    # 1. Decodificar el token para obtener el email
    email = verificar_token_verificacion(token)
    
    if not email:
        logger.error(f"Intento de verificación de correo con token inválido: {token}")
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enlace caducado</title>
</head>
<body style="font-family: ui-sans-serif, system-ui, sans-serif; background-color: #f8fafc; color: #334155; margin: 0; padding: 20px; display: flex; min-height: 90vh; align-items: center; justify-content: center; text-align: center;">

    <div style="background: white; max-width: 450px; width: 100%; padding: 32px 24px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
        
        <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
        
        <h1 style="color: #ef4444; font-size: 22px; font-weight: 800; margin-top: 0; margin-bottom: 12px; line-height: 1.3;">
            Enlace inválido o caducado
        </h1>
        
        <p style="font-size: 14px; color: #64748b; line-height: 1.6; margin-top: 0; margin-bottom: 28px; padding: 0 8px;">
            El enlace de verificación no es válido o ha expirado (24h). Por favor, intenta registrarte de nuevo.
        </p>
        
        <a href="/registro" style="background-color: #475569; color: white; padding: 14px 28px; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 15px; display: block; box-shadow: 0 4px 6px -1px rgba(71, 85, 105, 0.2); transition: background 0.2s;">
            Volver al registro
        </a>
        
    </div>

</body>
</html>
        """

    # 2. Buscar al usuario en la BBDD
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        logger.error(f"Intento de verificación de correo para email no encontrado: {email}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 3. Actualizar el estado
    if usuario.email_verificado:
        logger.debug(f"Intento de verificación de correo para usuario ya verificado: ID_USUARIO[{usuario.idusuario}]")
        mensaje = "Tu cuenta ya había sido verificada anteriormente."
    else:
        usuario.email_verificado = True
        db.commit()
        logger.info(f"Correo verificado para ID_USUARIO[{usuario.idusuario}]")
        enviar_solicitud_registro_telegram(usuario.email, usuario.nombre)
        mensaje = "¡Gracias! Tu correo ha sido verificado correctamente."

    # 4. Respuesta visual para el usuario
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro completado</title>
</head>
<body style="font-family: ui-sans-serif, system-ui, sans-serif; background-color: #f8fafc; color: #334155; margin: 0; padding: 20px; display: flex; min-height: 90vh; align-items: center; justify-content: center; text-align: center;">

    <div style="background: white; max-width: 450px; width: 100%; padding: 32px 24px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
        
        <div style="font-size: 48px; margin-bottom: 16px;">✅</div>
        
        <h1 style="color: #2563eb; font-size: 22px; font-weight: 800; margin-top: 0; margin-bottom: 12px; line-height: 1.3;">
            {mensaje}
        </h1>
        
        <p style="font-size: 14px; color: #64748b; line-height: 1.6; margin-top: 0; margin-bottom: 28px; padding: 0 8px;">
            Ahora un administrador debe activar tu cuenta manualmente para que puedas acceder al sistema.
        </p>
        
        <a href="/login" style="background-color: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 15px; display: block; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2); transition: background 0.2s;">
            Ir al Login
        </a>
        
    </div>

</body>
</html>
    """

@router.patch("/usuarios/{idusuario}/activar", dependencies=[Depends(verificar_admin)])
def activar_usuario(idusuario: int, estado: int, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    # Aquí buscaremos al usuario por ID y cambiaremos su campo activo a 1 o 2
    user = db.query(Usuario).filter(Usuario.idusuario == idusuario).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.activo = estado
    db.commit()
    logger.info(f"Usuario ID_USUARIO[{user.idusuario}] activado a nivel {estado}, por admin ID_ADMIN[{admin.idusuario}]")
    return {"msg": f"Usuario activado"}