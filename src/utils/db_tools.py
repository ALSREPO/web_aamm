from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import db_config, db_config_editor

URL_READ_ONLY = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
URL_WRITE = f"mysql+mysqlconnector://{db_config_editor['user']}:{db_config_editor['password']}@{db_config_editor['host']}:{db_config_editor['port']}/{db_config_editor['database']}"

# Creación de ambos Engines (Se crean una sola vez al arrancar la app)
engine_read_only = create_engine(
    URL_READ_ONLY,
    pool_pre_ping=True, # comprueba si ha perdido la conexion
    pool_recycle=3600, # Refresca las conexiones cada hora automáticamente
)
engine_write = create_engine(
    URL_WRITE,
    pool_pre_ping=True, # comprueba si ha perdido la conexion
    pool_recycle=3600, # Refresca las conexiones cada hora automáticamente
)

# Creación de Factorías de Sesiones independientes
SessionReadOnly = sessionmaker(autocommit=False, autoflush=False, bind=engine_read_only)
SessionWrite = sessionmaker(autocommit=False, autoflush=False, bind=engine_write)

Base = declarative_base()

def get_read_db():
    db = SessionReadOnly()
    try:
        yield db
    finally:
        db.close()

def get_write_db():
    db = SessionWrite()
    try:
        yield db
    finally:
        db.close()
