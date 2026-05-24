import logging
import os
import sys

# Importamos la configuración del LOG_LEVEL
from src.config import LOG_LEVEL

# Configurar el sistema de logs global
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AAMM-BBDD-INIT")

# Aseguramos que Python encuentre el módulo 'src' al ejecutar desde la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from src.utils.db_tools import get_engine

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")


def inicializar_base_de_datos():
    # Usamos los permisos de escritura/editor para aplicar cambios estructurales
    engine = get_engine(permisos="escritura")

    logger.info("--- [DB INIT] Iniciando comprobación de la Base de Datos ---")

    with engine.connect() as connection:
        # 1. Creamos la tabla de historial de migraciones si no existe
        connection.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS _schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
            )
        )
        connection.commit()

        # 2. Leer los archivos .sql disponibles en la carpeta scripts
        if not os.path.exists(SCRIPTS_DIR):
            logger.warning(f"[DB INIT] No se encontró la carpeta de scripts en: {SCRIPTS_DIR}")
            return

        sql_files = sorted([f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".sql")])

        # 3. Obtener cuáles ya se han ejecutado previamente
        result = connection.execute(text("SELECT version FROM _schema_migrations"))
        executed_versions = {row[0] for row in result}

        # 4. Ejecutar los scripts pendientes uno a uno
        for file_name in sql_files:
            if file_name in executed_versions:
                logger.debug(f"[DB INIT] Omitiendo: {file_name} (Ya aplicado anteriormente)")
                continue

            logger.info(f"[DB INIT] Aplicando script: {file_name}...")
            file_path = os.path.join(SCRIPTS_DIR, file_name)

            with open(file_path, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # Ejecutar el contenido del archivo SQL
            # Nota: Si el archivo tiene múltiples sentencias separadas por ';', 
            # las dividimos para ejecutarlas limpiamente.
            statements = sql_content.split(";")
            for statement in statements:
                statement = statement.strip()
                if statement:
                    connection.execute(text(statement))

            # Registrar en el historial que este archivo ya se aplicó con éxito
            connection.execute(
                text("INSERT INTO _schema_migrations (version) VALUES (:version)"),
                {"version": file_name},
            )
            connection.commit()
            logger.info(f"[DB INIT] ¡Éxito al aplicar {file_name}!")

    logger.info("--- [DB INIT] Base de datos actualizada y lista ---")


if __name__ == "__main__":
    inicializar_base_de_datos()