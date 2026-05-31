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
LOG_TAMANO_FICHERO = int(os.environ.get("LOG_TAMANO_FICHERO", 5))
LOG_NUM_FICHEROS_RESPALDO = int(os.environ.get("LOG_NUM_FICHEROS_RESPALDO", 3))

# 3. Configuración del token (JWT)
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_COOKIE_MAX_AGE = int(os.environ.get("ACCESS_TOKEN_COOKIE_MAX_AGE", 60))

# 4. Configuración de correo (Dinámica)
EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")
BASE_URL = os.environ.get("BASE_URL")

SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

# 5. Configuración para el listado de técnicas
ORDEN_LISTADO_TECNICAS = os.environ.get("ORDEN_LISTADO_TECNICAS", "fecha")
NUMERO_TECNICAS_POR_PAGINA = int(os.environ.get("NUMERO_TECNICAS_POR_PAGINA", 12))
SENTIDO_ORDEN_LISTADO_TECNICAS = os.environ.get("SENTIDO_ORDEN_LISTADO_TECNICAS", "desc")

RUTA_VIDEOS = os.environ.get("RUTA_VIDEOS", "/src/static/videos")
TAMANYO_MAXIMO_SUBIDA_VIDEOS = int(os.environ.get("TAMANYO_MAXIMO_SUBIDA_VIDEOS", 300)) # en MB

# 6. Configuración para Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID")