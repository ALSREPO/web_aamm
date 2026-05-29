import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.models.models import Disciplina, Etiqueta
from src.schemas.tecnicas import DisciplinaBase, EtiquetaBase
from src.utils.db_tools import get_read_db
from src.utils.auth import usuario_obligatorio

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