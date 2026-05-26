from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from datetime import date
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_password, crear_token_acceso, crear_token_verificacion, obtener_password_hash, enviar_correo_verificacion, verificar_admin
from src.models.models import Usuario
from src.schemas.autenticacion import UsuarioLogin, UsuarioCreate, Mensaje

router = APIRouter(
    prefix="/api/autenticacion",
    tags=["autenticación"]
)

import logging
logger = logging.getLogger("AAMM-APP-login")


# /login 
# /logout
# /registro
# /usuarios/{idusuario}/activar

@router.post("/login")
def login(response: Response, usuario: UsuarioLogin, db: Session = Depends(get_read_db)):
    # 1. Buscar usuario
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    
    # 2. Validar existencia y contraseña
    if not db_user or not verificar_password(usuario.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos."
        )
    
    # 3. Validar si el Email está Verificado ---
    if not db_user.email_verificado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes verificar tu correo electrónico antes de acceder. Revisa tu bandeja de entrada."
        )
    
    # 4. Verificar si está activo
    if db_user.activo == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está verificada, pero un administrador debe activarla manualmente."
        )
    
    # 5. Crear el Token
    access_token = crear_token_acceso(data={"sub": db_user.email})
    
    # 6. CREAR LA COOKIE (Lo nuevo)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,   # No accesible desde JS
        max_age=3600,    # 1 hora de duración
        expires=3600, 
        samesite="lax",  # Protección CSRF básica
        secure=False     # Cambiar a True cuando tengas HTTPS/SSL
    )
    
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
            logger.debug(f"Intento de registro con email ya verificado: {usuario.email}")
            raise HTTPException(status_code=400, detail="El email ya está registrado y verificado")
        
        # Si NO está verificado, actualizamos sus datos (por si cambió el nombre o pass)
        db_user.nombre = usuario.nombre
        db_user.password = obtener_password_hash(usuario.password)
        db_user.fechaCreacion = date.today()
        # No hace falta db.add, SQLAlchemy detecta el cambio
        logger.debug(f"Usuario actualizado: {usuario.email}")
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
        logger.debug(f"Nuevo usuario registrado: {usuario.email}")

    db.commit()
    
    # 2. Generar y enviar nuevo correo (esto sirve tanto para nuevos como para re-intentos)
    token = crear_token_verificacion(db_user.email)
    envio_ok = enviar_correo_verificacion(db_user.email, token)

    if not envio_ok:
        # Opcional: podrías decidir si borrar el usuario o avisar de un error
        logger.warning("Aviso: El correo no se pudo enviar")

    return {"message": "Si los datos son correctos, recibirás un correo para verificar tu cuenta."}



# pendiente verificar mail

@router.patch("/usuarios/{idusuario}/activar", dependencies=[Depends(verificar_admin)])
def activar_usuario(idusuario: int, estado: int, db: Session = Depends(get_write_db)):
    # Aquí buscaremos al usuario por ID y cambiaremos su campo activo a 1 o 2
    user = db.query(Usuario).filter(Usuario.idusuario == idusuario).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.activo = estado
    db.commit()
    return {"msg": f"Usuario actualizado a nivel {estado}"}