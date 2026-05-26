import logging
import contextvars

# Variable de contexto única
client_ip_ctx = contextvars.ContextVar("client_ip", default="sistema")

# Filtro inyector de IP mejorado y blindado contra KeyErrors
class IPInjectFilter(logging.Filter):
    def filter(self, record):
        # Si por lo que sea record no tiene el atributo, o el contexto falla,
        # nos aseguramos de inyectarlo para evitar el KeyError
        record.client_ip = client_ip_ctx.get()
        return True

def configurar_logs(log_level: str = "INFO"):
    # 1. Obtenemos el logger raíz (root)
    root_logger = logging.getLogger()
    
    # 2. Creamos el formateador con nuestra variable personalizada
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(client_ip)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 3. Configuramos el handler básico para que use nuestro filtro y formato
    handler = logging.StreamHandler()
    handler.addFilter(IPInjectFilter())  # <-- El filtro se añade DIRECTAMENTE al handler
    handler.setFormatter(formatter)
    
    # 4. Limpiamos handlers viejos si existieran (evita logs duplicados en Uvicorn)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))