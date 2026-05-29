import logging

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, text, desc, asc
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from src.models.models import Usuario, Disciplina, Etiqueta, Tecnica
from src.schemas.tecnicas import DisciplinaBase, EtiquetaBase, PaginaTecnicas
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_admin, usuario_obligatorio
from src.config import ORDEN_LISTADO_TECNICAS, SENTIDO_ORDEN_LISTADO_TECNICAS, NUMERO_TECNICAS_POR_PAGINA


router = APIRouter(prefix="/api/tecnicas", tags=["Técnicas"])

logger = logging.getLogger("AAMM-APP-tecnicas")

########################################
# /disciplinas        mostrar, insertar y eliminar
# /etiquetas          mostrar, insertar y eliminar
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
    nombre_normalizado = "".join(nombre.split()).upper()
    try:
        disciplina_existente = db.query(Disciplina).filter(func.upper(func.replace(Disciplina.disciplina, ' ', '')) == nombre_normalizado).first()
        if disciplina_existente:
            logger.warning(f"Intento de crear disciplina duplicada '{disciplina_existente.iddisciplina} - {disciplina_existente.disciplina}' por admin {admin.idusuario} - {admin.email}")
            raise HTTPException(status_code=400, detail="Disciplina ya existe")

        nueva = Disciplina(disciplina=nombre)
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        logger.info(f"Nueva disciplina creada {nueva.iddisciplina} - {nueva.disciplina}, por admin {admin.idusuario} - {admin.email}")
        return nueva
    except HTTPException:
        raise
    except Exception as err:
        logger.exception(f"Error creando disciplina '{nombre}' por admin {admin.idusuario} - {admin.email}: {err}")
        raise HTTPException(status_code=500, detail="Error al crear disciplina")

@router.post("/etiquetas", dependencies=[Depends(verificar_admin)])
def crear_etiqueta(nombre: str, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    nombre_normalizado = "".join(nombre.split()).upper()
    try:
        etiqueta_existente = db.query(Etiqueta).filter(func.upper(func.replace(Etiqueta.etiqueta, ' ', '')) == nombre_normalizado).first()
        if etiqueta_existente:
            logger.warning(f"Intento de crear etiqueta duplicada '{etiqueta_existente.idetiqueta} - {etiqueta_existente.etiqueta}' por admin {admin.idusuario} - {admin.email}")
            raise HTTPException(status_code=400, detail="Etiqueta ya existe")

        nueva = Etiqueta(etiqueta=nombre)
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        logger.info(f"Nueva etiqueta creada {nueva.idetiqueta} - {nueva.etiqueta}, por admin {admin.idusuario} - {admin.email}")
        return nueva
    except HTTPException:
        raise
    except Exception as err:
        logger.exception(f"Error creando etiqueta '{nombre}' por admin {admin.idusuario} - {admin.email}: {err}")
        raise HTTPException(status_code=500, detail="Error al crear etiqueta")

    
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



##################################

# Técnicas

@router.get("/", response_model=PaginaTecnicas, dependencies=[Depends(usuario_obligatorio)])
def listar_tecnicas(
    q: Optional[str] = Query(None),
    fecha: Optional[date] = Query(None),
    disciplina_id: List[int] = Query(None),
    etiqueta_id: List[int] = Query(None),
    ordenar_por: str = ORDEN_LISTADO_TECNICAS,
    sentido: str = SENTIDO_ORDEN_LISTADO_TECNICAS,
    skip: int = 0,
    limit: int = NUMERO_TECNICAS_POR_PAGINA,
    db: Session = Depends(get_read_db),
    # Usamos la dependencia que lanza 401 si no hay usuario
    usuario: Usuario = Depends(usuario_obligatorio) 
):
    # 1. Iniciamos la consulta con Eager Loading para que el JS no falle
    #query = db.query(Tecnica).options(
    #    joinedload(Tecnica.disciplinas),
    #    joinedload(Tecnica.etiquetas)
    #)
    query = db.query(Tecnica)
    
    # 2. Filtro de texto FULLTEXT
    if q:
        query = query.filter(
            text("MATCH(nombre, descripcion) AGAINST(:search IN BOOLEAN MODE)")
        ).params(search=f"*{q}*")
    
    # 3. Filtro por fecha exacta
    if fecha:
        query = query.filter(Tecnica.fecha == fecha)

    # 4. Filtros por Disciplinas (Lógica AND: debe cumplir todas las seleccionadas)
    if disciplina_id:
        for d_id in disciplina_id:
            query = query.filter(Tecnica.disciplinas.any(Disciplina.iddisciplina == d_id))
    
    # 5. Filtros por Etiquetas (Lógica AND)
    if etiqueta_id:
        for e_id in etiqueta_id:
            query = query.filter(Tecnica.etiquetas.any(Etiqueta.idetiqueta == e_id))
    
    # 6. Contar el total de resultados filtrados (Importante hacerlo antes del offset)
    total_filtrados = query.count()
    
    
    # 7. Ordenación Dinámica Segura
    campos_validos = {
        "id": Tecnica.idtecnica,
        "nombre": Tecnica.nombre,
        "fecha": Tecnica.fecha
    }
    
    campo_db = campos_validos.get(ordenar_por, Tecnica.fecha)
    criterio_orden = desc(campo_db) if sentido == "desc" else asc(campo_db)
    
    # 8. Traer solo la "página" actual con sus relaciones
    resultados = query.options(
        joinedload(Tecnica.disciplinas),
        joinedload(Tecnica.etiquetas)
    ).order_by(criterio_orden).offset(skip).limit(limit).all()

    # 9. Devolvemos el objeto que encaja con PaginaTecnicas
    return {
        "total": total_filtrados,
        "resultados": resultados
    }