import logging
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy import asc
from sqlalchemy.orm import Session
from typing import List

# Importaciones de tu ecosistema AAMM-APP
from src.models.horarios import HorarioClase  # Tu modelo de SQLAlchemy
from src.models.models import Usuario        # Para la dependencia de admin
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_admin, usuario_obligatorio

router = APIRouter(prefix="/api/horarios", tags=["Horarios"])

# Configuramos el logger con tu misma estructura de nombres
logger = logging.getLogger("AAMM-APP-horarios")

# Silenciamos los logs de debug del procesador de formularios multipart
logging.getLogger("multipart").setLevel(logging.WARNING)


###########################################################
# Función de utilidad para comprobar solapamientos de horarios (puede ser usada en el frontend o en la API)

def comprobar_solapamiento(db: Session, dia_semana: int, hora_inicio: str, hora_fin: str, idhorario_ignorar: int = None) -> bool:
    """
    Retorna True si la nueva clase se solapa con alguna existente el mismo día.
    """
    query = db.query(HorarioClase).filter(HorarioClase.dia_semana == dia_semana)
    
    if idhorario_ignorar:
        query = query.filter(HorarioClase.idhorario != idhorario_ignorar)
        
    clases_dia = query.all()
    
    # Convertimos las strings entrantes a formato de comparación limpia si es necesario, 
    # o dejamos que Python compare los objetos/strings de tiempo.
    for clase in clases_dia:
        # Formateamos a string "HH:MM" para asegurar una comparación exacta
        clase_ini = clase.hora_inicio.strftime("%H:%M") if hasattr(clase.hora_inicio, 'strftime') else str(clase.hora_inicio)
        clase_fin = clase.hora_fin.strftime("%H:%M") if hasattr(clase.hora_fin, 'strftime') else str(clase.hora_fin)
        
        # Fórmula de solapamiento: (Inicio1 < Fin2) AND (Fin1 > Inicio2)
        if hora_inicio < clase_fin and hora_fin > clase_ini:
            return True
            
    return False



###########################################################
# 🌐 1. Obtener todas las clases (Público para la APP)

@router.get("/", dependencies=[Depends(usuario_obligatorio)])
def obtener_todos_los_horarios(db: Session = Depends(get_read_db)):
    """
    Devuelve la lista completa de todas las clases programadas en la base de datos,
    ordenadas cronológicamente por la hora de inicio.
    """
    try:
        clases = db.query(HorarioClase).order_by(asc(HorarioClase.hora_inicio)).all()
        return clases
    except Exception as err:
        logger.exception(f"Error al obtener el listado de horarios: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al obtener el horario"
        )


###########################################################
# ➕ 2. Insertar nueva clase (Solo Administradores)

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
def crear_clase_horario(
    actividad: str = Form(...),
    dia_semana: int = Form(...),
    hora_inicio: str = Form(...),
    hora_fin: str = Form(...),
    db: Session = Depends(get_write_db),
    admin: Usuario = Depends(usuario_obligatorio)
):
    if dia_semana < 1 or dia_semana > 7:
        raise HTTPException(status_code=400, detail="El día de la semana debe estar entre 1 y 7")

    # 🛑 CONTROL DE SOLAPAMIENTO
    if comprobar_solapamiento(db, dia_semana, hora_inicio, hora_fin):
        logger.warning(f"Conflicto de horario detectado en POST por admin ID_ADMIN[{admin.idusuario}]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Existe otra clase en ese mismo rango de horario."
        )

    try:
        nueva_clase = HorarioClase(
            actividad=actividad,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )
        
        db.add(nueva_clase)
        db.commit()
        db.refresh(nueva_clase)
        
        logger.info(
            f"Nueva clase creada: ID_HORARIO[{nueva_clase.idhorario}] - '{nueva_clase.actividad}' "
            f"(Día {nueva_clase.dia_semana}, de {hora_inicio} a {hora_fin}) por admin ID_ADMIN[{admin.idusuario}]"
        )
        return nueva_clase

    except Exception as err:
        logger.exception(f"Error creando clase de horario '{actividad}' por admin ID_ADMIN[{admin.idusuario}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al crear la clase en el horario"
        )


###########################################################
# 🗑️ 3. Eliminar una clase (Solo Administradores)

@router.delete("/{idhorario}", dependencies=[Depends(verificar_admin)])
def borrar_clase_horario(
    idhorario: int, 
    db: Session = Depends(get_write_db), 
    admin: Usuario = Depends(usuario_obligatorio)
):
    """
    Elimina permanentemente una clase del horario mediante su ID único.
    """
    try:
        clase = db.query(HorarioClase).filter(HorarioClase.idhorario == idhorario).first()
        
        if not clase:
            logger.warning(f"Intento de borrado de clase no encontrada con id {idhorario}, por admin ID_ADMIN[{admin.idusuario}]")
            raise HTTPException(status_code=404, detail="La clase no existe en el horario")
            
        db.delete(clase)
        db.commit()
        
        logger.info(f"Clase de horario borrada exitosamente ID_HORARIO[{idhorario}] - '{clase.actividad}', por admin ID_ADMIN[{admin.idusuario}]")
        return {"ok": True, "detail": "Clase eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as err:
        logger.exception(f"Error al borrar clase ID_HORARIO[{idhorario}] por admin ID_ADMIN[{admin.idusuario}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al eliminar la clase del horario"
        )


###########################################################
# 📝 4. Editar una clase existente (Solo Administradores)

@router.put("/{idhorario}", dependencies=[Depends(verificar_admin)])
def actualizar_clase_horario(
    idhorario: int,
    actividad: str = Form(...),
    hora_inicio: str = Form(...),
    hora_fin: str = Form(...),
    db: Session = Depends(get_write_db),
    admin: Usuario = Depends(usuario_obligatorio)
):
    try:
        clase = db.query(HorarioClase).filter(HorarioClase.idhorario == idhorario).first()
        if not clase:
            raise HTTPException(status_code=404, detail="La clase no existe en el horario")
        
        # 🛑 CONTROL DE SOLAPAMIENTO (Pasamos su ID para que ignore su propio registro antiguo)
        if comprobar_solapamiento(db, clase.dia_semana, hora_inicio, hora_fin, idhorario_ignorar=idhorario):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La modificación genera un conflicto con otra clase existente."
            )

        info_antigua = f"'{clase.actividad}' ({clase.hora_inicio} - {clase.hora_fin})"
        
        clase.actividad = actividad
        clase.hora_inicio = hora_inicio
        clase.hora_fin = hora_fin
        
        db.commit()
        db.refresh(clase)
        
        logger.info(
            f"Clase de horario actualizada exitosamente ID_HORARIO[{idhorario}] por admin ID_ADMIN[{admin.idusuario}]. "
            f"Antes: {info_antigua} -> Ahora: '{clase.actividad}' ({hora_inicio} - {hora_fin})"
        )
        return clase

    except HTTPException:
        raise
    except Exception as err:
        logger.exception(f"Error al actualizar la clase ID_HORARIO[{idhorario}] por admin ID_ADMIN[{admin.idusuario}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la clase en el horario"
        )