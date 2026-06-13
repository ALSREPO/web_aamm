import logging

from fastapi import APIRouter, Depends, Query, HTTPException, status, BackgroundTasks
from sqlalchemy import func, text, desc, asc
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
import re

from src.models.models import Usuario, Disciplina, Etiqueta, Tecnica, Video
from src.schemas.tecnicas import DisciplinaBase, EtiquetaBase, PaginaTecnicas, TecnicaDetalle, TecnicaCreate, TecnicaRead
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_admin, usuario_obligatorio
from src.config import ORDEN_LISTADO_TECNICAS, SENTIDO_ORDEN_LISTADO_TECNICAS, NUMERO_TECNICAS_POR_PAGINA
from src.services.notificaciones import despachar_notificacion_evento

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
    return db.query(Etiqueta).order_by(Etiqueta.orden).all()


# Crear disciplinas y etiquetas
@router.post("/disciplinas", dependencies=[Depends(verificar_admin)])
def crear_disciplina(nombre: str, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    nombre_normalizado = "".join(nombre.split()).upper()
    try:
        disciplina_existente = db.query(Disciplina).filter(func.upper(func.replace(Disciplina.disciplina, ' ', '')) == nombre_normalizado).first()
        if disciplina_existente:
            logger.warning(f"Intento de crear disciplina duplicada '{disciplina_existente.iddisciplina} - {disciplina_existente.disciplina}' por admin ID_ADMIN[{admin.idusuario}]")
            raise HTTPException(status_code=400, detail="Disciplina ya existe")

        nueva = Disciplina(disciplina=nombre)
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        logger.info(f"Nueva disciplina creada {nueva.iddisciplina} - {nueva.disciplina}, por admin ID_ADMIN[{admin.idusuario}]")
        return nueva
    except HTTPException:
        raise
    except Exception as err:
        logger.exception(f"Error creando disciplina '{nombre}' por admin ID_ADMIN[{admin.idusuario}]: {err}")
        raise HTTPException(status_code=500, detail="Error al crear disciplina")

@router.post("/etiquetas", dependencies=[Depends(verificar_admin)])
def crear_etiqueta(nombre: str, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    nombre_normalizado = "".join(nombre.split()).upper()
    try:
        etiqueta_existente = db.query(Etiqueta).filter(func.upper(func.replace(Etiqueta.etiqueta, ' ', '')) == nombre_normalizado).first()
        if etiqueta_existente:
            logger.warning(f"Intento de crear etiqueta duplicada '{etiqueta_existente.idetiqueta} - {etiqueta_existente.etiqueta}' por admin ID_ADMIN[{admin.idusuario}]")
            raise HTTPException(status_code=400, detail="Etiqueta ya existe")

        nueva = Etiqueta(etiqueta=nombre)
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        logger.info(f"Nueva etiqueta creada {nueva.idetiqueta} - {nueva.etiqueta}, por admin ID_ADMIN[{admin.idusuario}]")
        return nueva
    except HTTPException:
        raise
    except Exception as err:
        logger.exception(f"Error creando etiqueta '{nombre}' por admin ID_ADMIN[{admin.idusuario}]: {err}")
        raise HTTPException(status_code=500, detail="Error al crear etiqueta")

    
# Borrar disciplinas y etiquetas
@router.delete("/disciplinas/{id}", dependencies=[Depends(verificar_admin)])
def borrar_disciplina(id: int, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    try:
        disciplina = db.query(Disciplina).filter(Disciplina.iddisciplina == id).first()
        db.query(Disciplina).filter(Disciplina.iddisciplina == id).delete()
        db.commit()
        logger.info(f"Disciplina borrada {id} - {disciplina.disciplina}, por admin ID_ADMIN[{admin.idusuario}]")
    except:
        logger.warning(f"Intento de borrado de disciplina no encontrada con id {id}, por admin ID_ADMIN[{admin.idusuario}]")
        raise HTTPException(status_code=404, detail="Disciplina no encontrada")
    
    return {"ok": True}

@router.delete("/etiquetas/{id}", dependencies=[Depends(verificar_admin)])
def borrar_etiqueta(id: int, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    try:
        etiqueta = db.query(Etiqueta).filter(Etiqueta.idetiqueta == id).first()
        db.query(Etiqueta).filter(Etiqueta.idetiqueta == id).delete()
        db.commit()
        logger.info(f"Etiqueta borrada {id} - {etiqueta.etiqueta}, por admin ID_ADMIN[{admin.idusuario}]")
    except:
        logger.warning(f"Intento de borrado de etiqueta no encontrada con id {id}, por admin ID_ADMIN[{admin.idusuario}]")
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")

    return {"ok": True}



##################################
#
# Listado de Técnicas para la página principal, con filtros y paginación
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
    usuario: Usuario = Depends(usuario_obligatorio) 
):
    # Volcado inicial de auditoría: Captura todos los parámetros de la Query String
    query_params_str = (
        f"q={q}&fecha={fecha}&disciplina_id={disciplina_id}&etiqueta_id={etiqueta_id}"
        f"&ordenar_por={ordenar_por}&sentido={sentido}&skip={skip}&limit={limit}"
    )
    logger.debug(f"ID_USUARIO[{usuario.idusuario}] - Petición entrante: GET /api/tecnicas/?{query_params_str}")

    try:
        # 1. Base de la consulta para el filtrado dinámico
        query = db.query(Tecnica)
        
        if q:
            # PASO 1: Sanitización estricta para evitar errores de sintaxis en MySQL BOOLEAN MODE
            q_sanitizada = re.sub(r'[+\-<>~*()"]', '', q)
            q_sanitizada = " ".join(q_sanitizada.split())
            
            if not q_sanitizada:
                q = None
                logger.warning(f"ID_USUARIO[{usuario.idusuario}] - El término de búsqueda 'q' quedó vacío tras la sanitización.")
        
        # 2. Aplicamos los filtros estándar
        if q:
            search_term = f"*{q_sanitizada}*"
            query = query.filter(
                text("MATCH(nombre, descripcion) AGAINST(:search IN BOOLEAN MODE)")
            ).params(search=search_term)
        
        if fecha:
            query = query.filter(Tecnica.fecha == fecha)

        if disciplina_id:
            for d_id in disciplina_id:
                query = query.filter(Tecnica.disciplinas.any(Disciplina.iddisciplina == d_id))
        
        if etiqueta_id:
            for e_id in etiqueta_id:
                query = query.filter(Tecnica.etiquetas.any(Etiqueta.idetiqueta == e_id))
        
        # 3. Total de filtrados
        total_filtrados = query.count()
        
        # 4. RESOLUCIÓN DE LA BÚSQUEDA Y ORDENACIÓN POR RELEVANCIA
        if q:
            # PASO A: Traemos idtecnica, nombre, descripción Y FECHA para poder ordenar en Python
            tecnicas_candidatas = query.with_entities(
                Tecnica.idtecnica, 
                Tecnica.nombre, 
                Tecnica.descripcion,
                Tecnica.fecha
            ).all()
            
            # PASO B: Calculamos el score y preparamos la lista para ordenar
            palabra_buscada = q_sanitizada.lower()
            lista_para_ordenar = []
            
            for id_tec, nombre, descr, fecha_tec in tecnicas_candidatas:
                # Score: Nombre x3 + Descripción x1
                score_nombre = len(re.findall(re.escape(palabra_buscada), nombre.lower())) * 3
                score_descr = len(re.findall(re.escape(palabra_buscada), descr.lower())) if descr else 0
                total_score = score_nombre + score_descr
                
                # Guardamos la tupla con todos los criterios necesarios
                lista_para_ordenar.append({
                    "id": id_tec,
                    "score": total_score,
                    "fecha": fecha_tec
                })
            
            # PASO C: ORDENACIÓN MULTINIVEL
            # Criterio 1: Score DESC (-x["score"])
            # Criterio 2: Fecha DESC (negamos el ordinal de la fecha)
            # Criterio 3: ID ASC (x["id"] sin negar)
            lista_para_ordenar.sort(key=lambda x: (
                -x["score"], 
                -(x["fecha"].toordinal() if x["fecha"] else 0), 
                x["id"]
            ))
            
            # PASO D: Paginación en Python
            pagina_ids = [item["id"] for item in lista_para_ordenar[skip : skip + limit]]
            
            if not pagina_ids:
                logger.info(f"ID_USUARIO[{usuario.idusuario}] - Búsqueda finalizada sin resultados para la página.")
                return {"total": total_filtrados, "resultados": []}
            
            # PASO E: Query final recuperando objetos completos
            resultados_desordenados = db.query(Tecnica).options(
                joinedload(Tecnica.disciplinas),
                joinedload(Tecnica.etiquetas)
            ).filter(Tecnica.idtecnica.in_(pagina_ids)).all()
            
            # PASO F: Reordenamos los objetos según el orden exacto de 'pagina_ids'
            mapa_resultados = {r.idtecnica: r for r in resultados_desordenados}
            resultados = [mapa_resultados[id_tec] for id_tec in pagina_ids if id_tec in mapa_resultados]

        else:
            # 5. FLUJO TRADICIONAL (Sin búsqueda por texto)
            campos_validos = {"id": Tecnica.idtecnica, "nombre": Tecnica.nombre, "fecha": Tecnica.fecha}
            campo_db = campos_validos.get(ordenar_por, Tecnica.fecha)
            criterio_orden = desc(campo_db) if sentido == "desc" else asc(campo_db)
            
            resultados = query.options(
                joinedload(Tecnica.disciplinas),
                joinedload(Tecnica.etiquetas)
            ).order_by(criterio_orden).offset(skip).limit(limit).all()

        logger.info(f"ID_USUARIO[{usuario.idusuario}] - ÉXITO: {total_filtrados} filtrados, {len(resultados)} devueltos.")

        return {"total": total_filtrados, "resultados": resultados}

    except Exception as e:
        logger.error(
            f"ID_USUARIO[{usuario.idusuario}] - ERROR CRÍTICO. "
            f"Filtros al buscar técnicas: {query_params_str}. Error: {str(e)}", 
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Error al procesar el listado de técnicas.")


# Obtener detalle de técnica (para la página de detalle, con sus vídeos, disciplinas y etiquetas)

@router.get("/{idtecnica}", response_model=TecnicaDetalle, dependencies=[Depends(usuario_obligatorio)])
def obtener_tecnica(idtecnica: int, db: Session = Depends(get_read_db), usuario: Usuario = Depends(usuario_obligatorio)):
    try:
        tecnica = db.query(Tecnica).options(
            joinedload(Tecnica.disciplinas),
            joinedload(Tecnica.etiquetas),
            joinedload(Tecnica.videos) # Carga la relación de vídeos
        ).filter(Tecnica.idtecnica == idtecnica).first()
        
        if not tecnica:
            logger.warning(f"ID_USUARIO[{usuario.idusuario}] Intento de acceso a técnica no encontrada con id {idtecnica}")
            raise HTTPException(status_code=404, detail="Técnica no encontrada")
        
        logger.info(f"ID_USUARIO[{usuario.idusuario}] Detalle de técnica {idtecnica} - {tecnica.nombre} obtenido exitosamente")
        return tecnica
    except Exception as e:
        logger.error(f"ID_USUARIO[{usuario.idusuario}] Error al obtener detalle de técnica {idtecnica}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener detalle de técnica")


# Crear nueva técnica (solo para admins, con disciplinas, etiquetas y vídeos asociados)

@router.post("/", response_model=TecnicaRead, dependencies=[Depends(verificar_admin)])
def crear_tecnica(
    obj_in: TecnicaCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_write_db), 
    admin: Usuario = Depends(usuario_obligatorio)
):
    try: 
        # 1. Crear la instancia básica de la Técnica
        nueva_tecnica = Tecnica(
            nombre=obj_in.nombre,
            descripcion=obj_in.descripcion,
            fecha=obj_in.fecha
        )

        # 2. Asociar Disciplinas
        if obj_in.disciplinas_ids:
            disciplinas = db.query(Disciplina).filter(Disciplina.iddisciplina.in_(obj_in.disciplinas_ids)).all()
            nueva_tecnica.disciplinas = disciplinas

        # 3. Asociar Etiquetas
        if obj_in.etiquetas_ids:
            etiquetas = db.query(Etiqueta).filter(Etiqueta.idetiqueta.in_(obj_in.etiquetas_ids)).all()
            nueva_tecnica.etiquetas = etiquetas

        # 4. Añadir a la sesión para obtener el ID
        db.add(nueva_tecnica)
        db.flush() # flush nos da el ID sin hacer commit definitivo todavía

        # 5. Crear los registros de Vídeos
        for nombre_fichero in obj_in.videos_nombres:
            nuevo_video = Video(
                video=nombre_fichero,
                idtecnica=nueva_tecnica.idtecnica
            )
            db.add(nuevo_video)

        # 6. Guardar todo en la BBDD
        db.commit()
        db.refresh(nueva_tecnica)
        logger.info(f"Técnica creada {nueva_tecnica.idtecnica} - {nueva_tecnica.nombre}, por admin ID_ADMIN[{admin.idusuario}]")

        # 7. LANZAR NOTIFICACIONES EN SEGUNDO PLANO 
        # Lo hacemos después del commit para garantizar que la técnica ya existe en la BBDD.
        try:
            despachar_notificacion_evento(
                db=db,
                background_tasks=background_tasks,
                nombre_evento="nuevo_video", # Mantenemos tu clave de evento
                titulo="🥋 ¡Nueva lección disponible!",
                cuerpo=f"Se ha subido la nueva técnica: '{nueva_tecnica.nombre}'.",
                ruta_destino=f"/tecnicas/{nueva_tecnica.idtecnica}" # 🚀 Apunta dinámicamente al ID recién creado
            )
            logger.info(f"Notificación en cola de BackgroundTasks para la técnica {nueva_tecnica.idtecnica}")
        except Exception as push_err:
            # Envolvemos esto en un try/except secundario para que, si por algún motivo
            # falla el despachador de push, el endpoint no rompa y devuelva la técnica al admin con éxito.
            logger.error(f"Error al encolar la notificación push para la técnica {nueva_tecnica.idtecnica}: {push_err}")
        
        return nueva_tecnica

    except Exception as e:
        logger.error(f"Error al crear técnica '{obj_in.nombre}' por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al crear técnica")


# Actualizar técnica (solo para admins, con disciplinas, etiquetas y vídeos asociados)

@router.put("/{idtecnica}", response_model=TecnicaRead, dependencies=[Depends(verificar_admin)])
def actualizar_tecnica(idtecnica: int, obj_in: TecnicaCreate, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):

    try:
        tecnica = db.query(Tecnica).filter(Tecnica.idtecnica == idtecnica).first()
        if not tecnica:
            raise HTTPException(status_code=404, detail="Técnica no encontrada")

        # Actualizar campos básicos
        tecnica.nombre = obj_in.nombre
        tecnica.descripcion = obj_in.descripcion
        tecnica.fecha = obj_in.fecha

        # Actualizar Relaciones (SQLAlchemy borra las antiguas y pone las nuevas automáticamente)
        tecnica.disciplinas = db.query(Disciplina).filter(Disciplina.iddisciplina.in_(obj_in.disciplinas_ids)).all()
        tecnica.etiquetas = db.query(Etiqueta).filter(Etiqueta.idetiqueta.in_(obj_in.etiquetas_ids)).all()

        # Actualizar Vídeos (Borramos los actuales y creamos los nuevos)
        db.query(Video).filter(Video.idtecnica == idtecnica).delete()
        for nombre_v in obj_in.videos_nombres:
            nuevo_v = Video(video=nombre_v, idtecnica=idtecnica)
            db.add(nuevo_v)

        db.commit()
        db.refresh(tecnica)
        logger.info(f"Técnica actualizada {tecnica.idtecnica} - {tecnica.nombre}, por admin ID_ADMIN[{admin.idusuario}]")
        return tecnica
    except Exception as e:
        logger.error(f"Error al actualizar técnica id {idtecnica} por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar técnica")


# Borrar técnica (solo para admins, con borrado en cascada de vídeos asociados)

@router.delete("/{idtecnica}", dependencies=[Depends(verificar_admin)])
def borrar_tecnica(idtecnica: int, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):

    try:
        tecnica = db.query(Tecnica).filter(Tecnica.idtecnica == idtecnica).first()
        
        if not tecnica:
            raise HTTPException(status_code=404, detail="Técnica no encontrada")

        # SQLAlchemy se encargará de borrar los vídeos asociados si pusiste 
        # cascade="all, delete-orphan" en la relación del modelo.
        db.delete(tecnica)
        db.commit()
        logger.info(f"Técnica borrada {tecnica.idtecnica} - {tecnica.nombre}, por admin ID_ADMIN[{admin.idusuario}]")
        return None
    except Exception as e:
        logger.error(f"Error al borrar técnica id {idtecnica} por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al borrar técnica")

