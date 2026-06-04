import logging
from logging.handlers import RotatingFileHandler
from src.config import LOG_TAMANO_FICHERO, LOG_NUM_FICHEROS_RESPALDO, LOG_FILE_PATH
import os
import contextvars

# Variable de contexto única (se mantiene intacta)
client_ip_ctx = contextvars.ContextVar("client_ip", default="sistema")

class IPInjectFilter(logging.Filter):
    def filter(self, record):
        record.client_ip = client_ip_ctx.get()
        return True

def configurar_logs(log_level: str = "INFO"):
    # 1. Aseguramos que exista la carpeta para el fichero de logs
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # 2. Obtenemos el logger raíz (root)
    root_logger = logging.getLogger()
    
    # El root logger debe aceptar el nivel más bajo (DEBUG)
    # y luego cada handler individual filtrará según lo que le pidamos.
    root_logger.setLevel(logging.DEBUG) 
    
    # 3. Formateador común para ambos (mantiene el campo client_ip)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(client_ip)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # --- HANDLER 1: CONSOLA (Terminal) ---
    console_handler = logging.StreamHandler()
    console_handler.addFilter(IPInjectFilter())
    console_handler.setFormatter(formatter)
    # Le asignamos el nivel que nos venga por parámetro (ej: INFO)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # --- HANDLER 2: ARCHIVO (Rotativo) ---
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, 
        maxBytes=LOG_TAMANO_FICHERO*1024*1024,  # 5 MB por archivo
        backupCount=LOG_NUM_FICHEROS_RESPALDO,         # Mantiene el actual y hasta 3 copias viejas (.log.1, .log.2...)
        encoding='utf-8'
    )
    file_handler.addFilter(IPInjectFilter())
    file_handler.setFormatter(formatter)
    # Al archivo podemos darle el mismo nivel, o forzarlo a guardar todo lo importante (INFO)
    file_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # 4. Limpiamos handlers viejos para evitar duplicados en entornos como Uvicorn
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # 5. Añadimos ambos canales al sistema central
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)