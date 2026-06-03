import logging
import os
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.utils.db_tools import get_read_db  # Tu dependencia de sesión de base de datos
from src.utils.auth import verificar_admin  # Tu control de acceso
from src.config import LOG_FILE_PATH
from src.models.models import Usuario

router = APIRouter(prefix="/api/logs", tags=["Admin Logs"])

logger = logging.getLogger("AAMM-APP-logs")

# Expresión regular para cazar ID_USUARIO[número] o ID_ADMIN[número]
PATRON_ID = re.compile(r"(ID_USUARIO|ID_ADMIN)\[(\d+)\]")


@router.get("/", dependencies=[Depends(verificar_admin)])
async def ver_logs_traducidos(
    db: Session = Depends(get_read_db),
    num_lineas: int = Query(default=500, ge=1, le=5000, alias="lineas")
):
    # 1. Si no existe ni el fichero base, es que no hay logs
    if not os.path.exists(LOG_FILE_PATH):
        return {"logs": ["El archivo de log aún no se ha creado."], "nombre_archivo": os.path.basename(LOG_FILE_PATH)}

    # 2. Traer usuarios optimizados para el mapa de traducción
    usuarios_db = db.query(Usuario).with_entities(Usuario.idusuario, Usuario.email, Usuario.nombre).all()
    mapa_usuarios = {str(u.idusuario): {"email": u.email, "nombre": u.nombre} for u in usuarios_db}

    def traducir_coincidencia(match):
        tipo_id = match.group(1)
        id_num = match.group(2)
        datos_usuario = mapa_usuarios.get(id_num)
        if datos_usuario:
            return f"{tipo_id}[{id_num} - {datos_usuario['nombre']} ({datos_usuario['email']})]"
        return f"{tipo_id}[{id_num} - ELIMINADO]"

    # 3. GENERAR LA LISTA DE ARCHIVOS EN ORDEN DE RECIENTE A ANTIGUO
    # Buscaremos en: archivo.log, archivo.log.1, archivo.log.2, archivo.log.3
    ficheros_a_revisar = [LOG_FILE_PATH]
    for i in range(1, 4):
        ruta_rotada = f"{LOG_FILE_PATH}.{i}"
        if os.path.exists(ruta_rotada):
            ficheros_a_revisar.append(ruta_rotada)

    lineas_crudas = []

    # 4. LEER EN CASCADA HASTA LLENAR EL CUPO PEDIDO
    for ruta in ficheros_a_revisar:
        # Si ya tenemos todas las líneas que nos ha pedido el frontend, paramos de leer archivos
        if len(lineas_crudas) >= num_lineas:
            break
            
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                lineas_fichero = f.readlines()
                
                # Necesitamos saber cuántas líneas nos faltan para cumplir el cupo
                cuantas_faltan = num_lineas - len(lineas_crudas)
                
                # Cogemos las últimas 'cuantas_faltan' líneas de este archivo
                ultimas_del_fichero = lineas_fichero[-cuantas_faltan:]
                
                # Como leemos de más nuevo a más antiguo, las líneas de las rotaciones
                # deben acumularse al FINAL de nuestra lista temporal
                lineas_crudas.extend(ultimas_del_fichero)
        except Exception as e:
            # Si un archivo está bloqueado o da error de lectura, saltamos al siguiente
            continue

    # 5. INVERTIR Y TRADUCIR (Para que lo más NUEVO de todo salga arriba en la pantalla)
    lineas_crudas.reverse()

    logs_traducidos = []
    for linea in lineas_crudas:
        linea = linea.strip()
        if linea:
            linea_traducida = PATRON_ID.sub(traducir_coincidencia, linea)
            logs_traducidos.append(linea_traducida)

    return {"logs": logs_traducidos}