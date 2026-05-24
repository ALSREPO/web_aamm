import os

from dotenv import load_dotenv

load_dotenv(override=False)

# 1. Configuración de la conexión a la base de datos (Dinámica)
db_config = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "user_defecto"),
    "password": os.environ.get("DB_PASSWORD", "pass_defecto"),
    "database": os.environ.get("DB_NAME", "database_defecto"),
    "port": int(os.environ.get("DB_PORT", 3306)),
}

db_config_editor = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER_EDITOR", "user_defecto"),
    "password": os.environ.get("DB_PASSWORD_EDITOR", "pass_defecto"),
    "database": os.environ.get("DB_NAME", "database_defecto"),
    "port": int(os.environ.get("DB_PORT", 3306)),
}

# 2. Configuración del nivel de logs (Dinámica)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()