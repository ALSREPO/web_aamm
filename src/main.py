from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import text  # <-- CORREGIDO: Faltaba esta importación

print('HOLA')

# Forzamos el import limpio según la estructura de tu proyecto
from src.utils.db_tools import fetch_test_rows, get_engine
print('ENTRA 1')

engine = get_engine()
print(f'engine :  {engine}')

with engine.connect() as connection:
    query = text("SELECT * FROM test")
    resultado = connection.execute(query)
    filas = resultado.fetchall()
    if not filas:
        print("Conexión exitosa, pero la tabla 'test' está vacía.")
    else:
        print(f"¡Éxito! Se encontraron {len(filas)} filas:")
        for fila in filas:
            print(fila)

app = FastAPI(title="AAMM - Artes Marciales")


def render_test_rows_html(result):
    if not result["ok"]:
        return f"<p style='color:#fca5a5;'>Error al cargar las filas: {result['error']}</p>"

    rows = result["rows"]
    if not rows:
        return "<p>No hay filas en la tabla <code>test</code>.</p>"

    headers = list(rows[0].keys())
    header_html = "".join(f"<th>{header}</th>" for header in headers)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{row.get(header, '')}</td>" for header in headers) + "</tr>"
        for row in rows
    )

    return f"""
    <table style="width:100%; border-collapse: collapse; margin-top:1rem;">
        <thead>
            <tr>{header_html}</tr>
        </thead>
        <tbody>
            {body_html}
        </tbody>
    </table>
    """


@app.get("/", response_class=HTMLResponse)
def index():
    result = fetch_test_rows()
    table_html = render_test_rows_html(result)

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8" />
        <title>AAMM</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 2rem;
                background: #0f172a;
                color: #f8fafc;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: #111827;
                border-radius: 18px;
                padding: 2rem;
                box-shadow: 0 12px 30px rgba(15, 23, 42, 0.35);
            }}
            h1 {{
                color: #f59e0b;
                margin-bottom: 0.5rem;
            }}
            p {{
                line-height: 1.6;
                color: #cbd5e1;
            }}
            table {{
                background: #111827;
                border: 1px solid #334155;
            }}
            th, td {{
                border: 1px solid #334155;
                padding: 0.75rem;
                text-align: left;
                color: #e2e8f0;
            }}
            th {{
                background: #1e293b;
            }}
            .badge {{
                display: inline-block;
                margin-top: 1rem;
                padding: 0.4rem 0.8rem;
                border-radius: 999px;
                background: #1d4ed8;
                color: #eff6ff;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Artes Marciales AAMM</h1>
            <p>Esta es la página inicial usando la configuración dinámica de <code>.env</code>.</p>
            <p>Se están mostrando las filas actuales de la tabla <code>test</code>.</p>
            {table_html}
            <div class="badge">FastAPI + SQLAlchemy + MySQL</div>
        </div>
    </body>
    </html>
    """


@app.get("/tecnicas")
def tecnicas():
    return fetch_test_rows()


if __name__ == "__main__":
    import uvicorn
    # Cambiado a 0.0.0.0 para que escuche fuera del contenedor si lo corres directo
    uvicorn.run("src.main:app", host="0.0.0.0", port=8888, reload=True)