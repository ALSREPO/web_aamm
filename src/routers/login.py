from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from src.utils.db_tools import get_read_db
from src.utils.auth import verificar_password, crear_token_acceso
from src.models import models
from src.schemas import autenticacion

router = APIRouter(
    prefix="/api/autenticacion",
    tags=["autenticación"]
)

@router.post("/login")
def login(response: Response, usuario: autenticacion.UsuarioLogin, db: Session = Depends(get_read_db)):
    # 1. Buscar usuario
    db_user = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    
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