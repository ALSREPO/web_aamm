import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.models.models import Usuario, Disciplina, Etiqueta
from src.schemas.tecnicas import DisciplinaBase, EtiquetaBase
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_admin, usuario_obligatorio

router = APIRouter(prefix="/api/tecnicas", tags=["Técnicas"])

logger = logging.getLogger("AAMM-APP-tecnicas")

########################################
# /disciplinas        mostrar disciplinas
# /etiquetas          mostrar etiquetas
# 
########################################


# mostrar las discriplinas y etiquetas 
@router.get("/disciplinas", response_model=list[DisciplinaBase], dependencies=[Depends(usuario_obligatorio)])
def obtener_disciplinas(db: Session = Depends(get_read_db)):
    return db.query(Disciplina).all()

@router.get("/etiquetas", response_model=list[EtiquetaBase], dependencies=[Depends(usuario_obligatorio)])
def obtener_etiquetas(db: Session = Depends(get_read_db)):
    return db.query(Etiqueta).all()

# Crear disciplinas y etiquetas
@router.post("/disciplinas", dependencies=[Depends(verificar_admin)])
def crear_disciplina(nombre: str, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    nueva = Disciplina(disciplina=nombre)
    db.add(nueva)
    db.commit()
    logger.info(f"Nueva disciplina creada {nueva.iddisciplina} - {nueva.disciplina}, por admin {admin.idusuario} - {admin.email}")
    return nueva

@router.post("/etiquetas", dependencies=[Depends(verificar_admin)])
def crear_etiqueta(nombre: str, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    nueva = Etiqueta(etiqueta=nombre)
    db.add(nueva)
    db.commit()
    logger.info(f"Nueva etiqueta creada {nueva.idetiqueta} - {nueva.etiqueta}, por admin {admin.idusuario} - {admin.email}")
    return nueva