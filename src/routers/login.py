from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from src.utils.db_tools import get_read_db
from src.utils.auth import verificar_password
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
    
    return {"message": "Login exitoso", "redirect": "/"}