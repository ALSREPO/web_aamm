from sqlalchemy import create_engine, text


from src.config import db_config, db_config_editor


def get_engine(permisos="lectura"):
    cfg = db_config_editor if permisos == "escritura" else db_config

    print(f"get engine: {permisos} - mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}")

    return create_engine(
        f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}",
        pool_pre_ping=True,
    )


def fetch_test_rows():
    engine = get_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM test ORDER BY 1"))
            rows = [dict(row._mapping) for row in result]
            return {"ok": True, "rows": rows}
    except Exception as exc:
        return {"ok": False, "rows": [], "error": str(exc)}
