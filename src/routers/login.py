import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta, timezone
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_password, crear_token_acceso, crear_token_verificacion, verificar_token_verificacion, obtener_password_hash, enviar_correo_verificacion, verificar_admin, usuario_obligatorio
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
        logger.warning(f"Intento de login fallido para email: {db_user.idusuario if db_user else 'N/A'} - {usuario.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos."
        )
    
    # 3. Validar si el Email está Verificado ---
    if not db_user.email_verificado:
        logger.warning(f"Intento de login con email no verificado para {db_user.idusuario} - {db_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes verificar tu correo electrónico antes de acceder. Revisa tu bandeja de entrada."
        )
    
    # 4. Verificar si está activo
    if db_user.activo == 0:
        logger.warning(f"Intento de login con cuenta inactiva para {db_user.idusuario} - {db_user.email}")
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

    logger.info(f"Login exitoso para {db_user.idusuario} - {db_user.email}")
    
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
            logger.debug(f"Intento de registro con email ya verificado: {db_user.idusuario} - {usuario.email}")
            raise HTTPException(status_code=400, detail="El email ya está registrado y verificado")
        
        # Si NO está verificado, actualizamos sus datos (por si cambió el nombre o pass)
        db_user.nombre = usuario.nombre
        db_user.password = obtener_password_hash(usuario.password)
        db_user.fechaCreacion = date.today()
        # No hace falta db.add, SQLAlchemy detecta el cambio
        logger.debug(f"Usuario actualizado: {db_user.idusuario} - {usuario.email}")
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
        logger.debug(f"Nuevo usuario registrado: {db_user.idusuario} - {usuario.email}")

    db.commit()
    
    # 2. Generar y enviar nuevo correo (esto sirve tanto para nuevos como para re-intentos)
    token = crear_token_verificacion(db_user.email)
    envio_ok = enviar_correo_verificacion(db_user.email, token)

    if not envio_ok:
        # Opcional: podrías decidir si borrar el usuario o avisar de un error
        logger.warning(f"Aviso: El correo para verificar la cuenta de {db_user.idusuario} - {db_user.email} no se pudo enviar")

    return {"message": "Si los datos son correctos, recibirás un correo para verificar tu cuenta."}



@router_raiz.get("/verificar_mail", response_class=HTMLResponse)
def verificar_mail(token: str = Query(...), db: Session = Depends(get_write_db)):
    # 1. Decodificar el token para obtener el email
    email = verificar_token_verificacion(token)
    
    if not email:
        logger.warning(f"Intento de verificación de correo con token inválido: {token}")
        return """
        <html>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1 style="color: #ef4444;">⚠️ Enlace inválido o caducado</h1>
                <p>El enlace de verificación no es válido o ha expirado (24h). Por favor, intenta registrarte de nuevo.</p>
                <a href="/registro">Volver al registro</a>
            </body>
        </html>
        """

    # 2. Buscar al usuario en la BBDD
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        logger.warning(f"Intento de verificación de correo para email no encontrado: {email}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 3. Actualizar el estado
    if usuario.email_verificado:
        logger.debug(f"Intento de verificación de correo para usuario ya verificado: {usuario.idusuario} - {email}")
        mensaje = "Tu cuenta ya había sido verificada anteriormente."
    else:
        usuario.email_verificado = True
        db.commit()
        logger.info(f"Correo verificado para {usuario.idusuario} - {usuario.email}")
        mensaje = "¡Gracias! Tu correo ha sido verificado correctamente."

    # 4. Respuesta visual para el usuario
    return f"""
    <html>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h1 style="color: #10b981;">✅ {mensaje}</h1>
            <p>Ahora un administrador debe activar tu cuenta manualmente para que puedas acceder.</p>
            <br>
            <a href="/login" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ir al Login</a>
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
    logger.info(f"Usuario {user.idusuario} - {user.email} activado a nivel {estado}, por admin {admin.idusuario} - {admin.email}")
    return {"msg": f"Usuario activado"}