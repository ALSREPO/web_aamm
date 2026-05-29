import logging

from fastapi import APIRouter, Depends, Query, HTTPException
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

    
# Borrar disciplinas y etiquetas
@router.delete("/disciplinas/{id}", dependencies=[Depends(verificar_admin)])
def borrar_disciplina(id: int, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    try:
        disciplina = db.query(Disciplina).filter(Disciplina.iddisciplina == id).first()
        db.query(Disciplina).filter(Disciplina.iddisciplina == id).delete()
        db.commit()
        logger.info(f"Disciplina borrada {id} - {disciplina.disciplina}, por admin {admin.idusuario} - {admin.email}")
    except:
        logger.warning(f"Intento de borrado de disciplina no encontrada con id {id}, por admin {admin.idusuario} - {admin.email}")
        raise HTTPException(status_code=404, detail="Disciplina no encontrada")
    
    return {"ok": True}

@router.delete("/etiquetas/{id}", dependencies=[Depends(verificar_admin)])
def borrar_etiqueta(id: int, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    try:
        etiqueta = db.query(Etiqueta).filter(Etiqueta.idetiqueta == id).first()
        db.query(Etiqueta).filter(Etiqueta.idetiqueta == id).delete()
        db.commit()
        logger.info(f"Etiqueta borrada {id} - {etiqueta.etiqueta}, por admin {admin.idusuario} - {admin.email}")
    except:
        logger.warning(f"Intento de borrado de etiqueta no encontrada con id {id}, por admin {admin.idusuario} - {admin.email}")
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")

    return {"ok": True}