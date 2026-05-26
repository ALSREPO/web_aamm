from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.utils.db_tools import get_read_db
from src.models import models

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


##########################
# listado de usuarios

@router.get("/listado-completo")
def listar_usuarios(db: Session = Depends(get_read_db)):
    return db.query(models.Usuario).all()
    