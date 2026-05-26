import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_admin
from src.models.models import Usuario

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])

logger = logging.getLogger("AAMM-APP-usuarios")

########################################
# /listado-completo
# /cambiar-estatus/{idusuario}

@router.get("/listado-completo")
def listar_usuarios(db: Session = Depends(get_read_db)):
    return db.query(Usuario).all()


@router.put("/cambiar-estatus/{idusuario}", dependencies=[Depends(verificar_admin)])
def cambiar_estatus(idusuario: int, nuevo_nivel: int, db: Session = Depends(get_write_db)):
    usuario = db.query(Usuario).filter(Usuario.idusuario == idusuario).first()
    if not usuario: raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.activo = nuevo_nivel
    db.commit()
    logger.info(f"Usuario {usuario.email} actualizado a nivel {nuevo_nivel}")
    return {"ok": True}