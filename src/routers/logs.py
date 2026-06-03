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
    # Añadimos el parámetro con un valor por defecto de 500
    num_lineas: int = Query(default=500, ge=1, le=5000, alias="lineas")
):
    if not os.path.exists(LOG_FILE_PATH):
        return {"logs": ["El archivo de log aún no se ha creado."]}

    # 1. OPTIMIZACIÓN: Traemos solo idusuario, email y nombre para no cargar objetos pesados en memoria
    usuarios_db = db.query(Usuario).with_entities(Usuario.idusuario, Usuario.email, Usuario.nombre).all()

    # 2. Construimos el mapa guardando un diccionario por usuario
    # Así tenemos accesibles tanto el email como el nombre por separado
    mapa_usuarios = {
        str(u.idusuario): {"email": u.email, "nombre": u.nombre} 
        for u in usuarios_db
    }

    logs_traducidos = []

    # 3. Función auxiliar que reemplazará el ID por: ID - Nombre (Email)
    def traducir_coincidencia(match):
        tipo_id = match.group(1)  # ID_USUARIO o ID_ADMIN
        id_num = match.group(2)   # El número (ej: 24)
        
        # Buscamos en nuestro mapa de la BBDD.
        datos_usuario = mapa_usuarios.get(id_num)
        
        if datos_usuario:
            nombre = datos_usuario["nombre"]
            email = datos_usuario["email"]
            return f"{tipo_id}[{id_num} - {nombre} ({email})]"
        else:
            # Si no existe en el mapa, es que el registro fue eliminado físicamente de la BBDD
            return f"{tipo_id}[{id_num} - ELIMINADO]"

    # 4. Leer el archivo (últimas n líneas)
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        lineas = f.readlines()[-num_lineas:]

        # Opcional: Invertimos el orden para que lo más NUEVO salga arriba del todo en la web
        lineas.reverse()
        
        for linea in lineas:
            linea = linea.strip()
            if linea:
                # Aplicamos la traducción con la expresión regular
                linea_traducida = PATRON_ID.sub(traducir_coincidencia, linea)
                logs_traducidos.append(linea_traducida)

    return {"logs": logs_traducidos}