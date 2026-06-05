# Biblioteca de Técnicas de Artes Marciales (AAMM)

Aplicación web para la gestión, consulta y visualización de técnicas de artes marciales con soporte multimedia y control de accesos por roles.

## 🌐 Acceso a la Aplicación
Se puede acceder a través de la siguiente URL:
👉 **[https://aamm.alsdev.com](https://aamm.alsdev.com)**

---

## 🚀 Características Principales

### Para Usuarios
* **Diseño Moderno y Adaptable:** Interfaz Web Responsive optimizada al milímetro para móviles, tablets y ordenadores.
* **Modo Oscuro Integrado:** Selector nativo para conmutar fácilmente entre interfaz clara y oscura.
* **Sistema de Autenticación Seguro:** * Registro de usuarios con validación de identidad mediante envío de email de verificación.
  * Inicio de sesión protegido utilizando cookies de seguridad cifradas (`HttpOnly`).
  * Panel de perfil con opciones para cambiar contraseña y eliminación definitiva de la cuenta.
* **Buscador Avanzado y Biblioteca:** Consulta rápida de técnicas con filtrado dinámico, ordenación y sistema de paginación eficiente.
* **Fichas de Detalle Multimedia:** Visualización interactiva de cada técnica, taxonomías asociadas y reproductor de vídeo integrado con medidas que dificultan la descarga directa del archivo.
* **Parrilla de Horarios:** Consulta pública de los horarios y clases de la escuela organizados por días de la semana.
* **Sección Acerca de:** Información corporativa y detalles técnicos sobre la plataforma web.

### Para Administradores (Panel de Control)
* **Gestión de Técnicas:** Control total para crear, editar y borrar las técnicas del catálogo.
* **Gestión de Usuarios:** Panel administrativo para activar cuentas, banear infractores, forzar cambios de contraseña o eliminar usuarios.
* **Mantenimiento de Taxonomías:** Herramientas para añadir y purgar Disciplinas y Etiquetas.
* **Administración Multimedia:** Subida directa de archivos de vídeo al servidor y borrado físico de los mismos.
* **Control de Horarios:** Panel específico para añadir y editar clases en línea con flujos de trabajo protegidos contra borrados accidentales.
* **Automatización con Telegram:** Notificación instantánea en canal de Telegram cuando un usuario valida su mail, permitiendo su activación en el sistema directamente haciendo clic desde la propia app de Telegram.
* **Monitorización del Sistema:** Pantalla web de visualización de logs en tiempo real respaldada por un sistema de log dual (escritura simultánea en la terminal de salida y en ficheros de disco duro).
---

## 📁 Estructura del Proyecto

```text
.
├── database/                     # Inicialización y versionado de la Base de Datos
│   ├── init_db.py                # Script Python para la ejecución de las migraciones
│   └── scripts/                  # Scripts SQL ordenados cronológicamente
│       ├── 0000_inicializar_bbdd_prueba.sql
│       ├── 0001_create_ta_usuarios.sql
│       ├── 0002_insert_ta_usuarios_prueba.sql
│       ├── 0003_create_tablas_tecnicas.sql
│       ├── 0004_insert_ta_usuarios_ta_tecnicas.sql
│       ├── 0005_create_tabla_horarios.sql
│       └── 0006_insert_ta_horarios.sql
├── logs/                         # Almacenamiento de trazas de ejecución en disco
│   └── aamm_ejecucion.log
├── src/                          # Código fuente de la aplicación (FastAPI)
│   ├── main.py                   # Punto de entrada y montaje de la aplicación
│   ├── config.py                 # Gestión de variables de entorno y propiedades
│   ├── models/                   # Modelos de datos de SQLAlchemy
│   │   ├── models.py             # Modelos de usuarios, técnicas y taxonomías
│   │   └── horarios.py           # Modelos de la parrilla de horarios
│   ├── routers/                  # Enrutadores y endpoints de la API (Endpoints CRUD)
│   │   ├── frontEnd.py           # Rutas del servidor que sirven las vistas HTML
│   │   ├── login.py              # Lógica de autenticación, registro y sesiones
│   │   ├── usuarios.py           # Gestión y administración de usuarios
│   │   ├── tecnicas.py           # Motor de búsqueda y edición de técnicas
│   │   ├── videos.py             # Lógica de transmisión y seguridad de vídeos
│   │   ├── horarios.py           # Gestión del calendario escolar
│   │   └── logs.py               # Endpoint para la lectura del fichero de trazas
│   ├── schemas/                  # Esquemas de validación de datos (Pydantic)
│   │   ├── autenticacion.py
│   │   └── tecnicas.py
│   ├── static/                   # Archivos estáticos consumidos por el navegador
│   │   ├── css/                  # Hojas de estilo (Tailwind CSS compilado)
│   │   │   ├── input.css
│   │   │   └── styles.css
│   │   ├── js/                   # Controladores interactivos Vanilla JS (ES6+)
│   │   │   ├── horarios/         # Gestión del panel de horarios
│   │   │   ├── logs/             # Lógica del lector de logs en tiempo real
│   │   │   ├── partials/         # Componentes comunes (Navbar global)
│   │   │   ├── tecnicas/         # Controladores de búsqueda, tablas y edición
│   │   │   └── usuarios/         # Controladores de login, registro, perfiles y admin
│   │   └── favicon.ico           # Identificadores visuales del sitio
│   ├── templates/                # Vistas HTML renderizadas en servidor (Jinja2)
│   │   ├── base.html             # Plantilla contenedora global
│   │   ├── index.html            # Biblioteca de técnicas principal (Home)
│   │   ├── acerca_de.html        # Sección informativa
│   │   ├── horarios/             # Vistas pública y de gestión de horarios
│   │   ├── logs/                 # Panel de monitorización de logs de admin
│   │   ├── partials/             # Elementos fragmentados reutilizables (_navbar, _footer)
│   │   ├── tecnicas/             # Detalle y formularios de técnicas
│   │   └── usuarios/             # Login, registro, perfil y control de cuentas
│   └── utils/                    # Componentes transversales de utilidad
│       ├── auth.py               # Encriptación de contraseñas (bcrypt) y gestión de JWT
│       ├── db_tools.py           # Factoría de conexiones a bases de datos
│       ├── logging_config.py     # Configuración del Logger Dual (Consola + Archivo)
│       └── telegram.py           # Conector e integraciones con la API del Bot de Telegram
├── videos_privados/              # Directorio local restringido para el almacenamiento físico de vídeos
├── Dockerfile                    # Receta de empaquetado y contenedorización para producción
├── requirements.txt              # Manifiesto de librerías y dependencias de Python
└── LICENSE                       # Licencia legal del proyecto
```

---

## 🛠️ Tecnologías Utilizadas
* **Backend**: Python 3.10+, FastAPI (Asíncrono), Uvicorn.
* **Base de Datos**: SQL Server / MySQL (gestionado mediante SQLAlchemy ORM).
* **Seguridad**: Tokens JWT (PyJWT), Hashes seguros con Passlib (bcrypt), Cookies HttpOnly / Secure Flags.
* **Frontend**: HTML5, Jinja2 Templates, Tailwind CSS (Layout adaptable y soporte nativo Dark Mode) y JavaScript vanilla (ES6+).
* **Integraciones**: Telegram Bot API para administración remota.
* **Despliegue**: Docker, Cloudflare (CDN/Proxy y caché).


---

## 🛠️ YAML para despliegue desde Docker, en Producción y Staging

```YAML
version: '3.8'

services:
  aamm-app:
    build: 
      context: https://github.com/ALSREPO/web_aamm.git#main
      dockerfile: Dockerfile
    container_name: aamm-app
    restart: always
    labels:
      - "com.centurylinklabs.watchtower.enable=false"
    
    # Variables de sistema
    environment:
      - TZ=Europe/Madrid
      - PYTHONUNBUFFERED=1  # Solución para los prints
      
      # Configuración de la BBDD
      - DB_HOST=xxxx
      - DB_USER=xxxx
      - DB_PASSWORD=xxxx
      - DB_USER_EDITOR=xxxx
      - DB_PASSWORD_EDITOR=xxxx
      - DB_NAME=xxxx
      - DB_PORT=3306
      
      # Configuración del logger
      - LOG_LEVEL=DEBUG # INFO / DEBUG
      - LOG_TAMANO_FICHERO=5 # en MB
      - LOG_NUM_FICHEROS_RESPALDO=3 # 3 copias + el actual, no supera los 20MB (5MB * 4 ficheros)
      - LOG_FILE_PATH=logs/aamm_ejecucion.log
      
      # Configuración de inicio de sesión (login)
      - SECRET_KEY=xxxx
      - ALGORITHM=HS256
      - ACCESS_TOKEN_COOKIE_MAX_AGE=2678400 # en segundos, cuanto dura la sesión del usuario, aquí 31 días (31*24*3600 = 2678400)

      # Configuración de servidor de correo
      - EMAIL_EMISOR=no-reply@alsdev.com
      - BASE_URL=https://aamm.alsdev.com
      - SMTP_SERVER=smtp-relay.brevo.com
      - SMTP_PORT=587
      - SMTP_USERNAME=xxxx@smtp-brevo.com
      - SMTP_PASSWORD=xsmtpsib-xxxx
      
      # Configuración para el listado de técnicas
      - ORDEN_LISTADO_TECNICAS=fecha
      - NUMERO_TECNICAS_POR_PAGINA=12
      - SENTIDO_ORDEN_LISTADO_TECNICAS=desc
      
      # Configuración vídeos
      - RUTA_VIDEOS=videos_privados
      - TAMANYO_MAXIMO_SUBIDA_VIDEOS=300 # en MB

      # Configuración del bot de Telegram para notificaciones
      - TELEGRAM_BOT_TOKEN=xxxx
      - TELEGRAM_ADMIN_CHAT_ID=xxxx
      - TELEGRAM_BOT_API_KEY=xxxx # aleatoria, ejecutar en bash: python3 -c "import secrets; print(secrets.token_urlsafe(32))"

      # MOSTRAR/OCULTAR HORARIO
      - MOSTRAR_HORARIO=1 # 0 para ocultar el horario, 1 para mostrarlo

    volumes:
      # MAPEAMOS LOS VÍDEOS
      - /directorio/local/videos:/app/videos_privados
      # Guarda los paquetes de pip en un volumen seguro de Docker
      - cache_static:/app/static
      
    dns:
      - 8.8.8.8
      - 8.8.4.4
    extra_hosts:
      - "host.docker.internal:host-gateway"
    ports:
      - "8892:8888"  
    networks:
      - red_publica

volumes:
  cache_static: # Espacio aislado para los archivos estáticos

networks:
  red_publica:
    external: true
```


---

## 🛠️ YAML para despliegue desde Docker, en Develop

```YAML
version: '3.8'

services:
  aamm-app-dev:
    #  Usamos una imagen base de Python (usa la versión que necesites, ej: 3.10-slim o python:3.11)
    image: python:3.10-slim  
    container_name: aamm-app-dev
    restart: always
    labels:
      - "com.centurylinklabs.watchtower.enable=false"
    
    # Comando para que el contenedor instale tus librerías y arranque la app en vivo
    # Modifica "app.py" por el nombre de tu archivo principal (ej: index.py, main.py...)
    # sh -c "apt-get update && apt-get install -y build-essential && # poner esta linea dentro del command: >
    command: >
      sh -c "pip install --no-cache-dir -r /app/requirements.txt && 
             python /app/database/init_db.py &&
             uvicorn src.main:app --host 0.0.0.0 --port 8888 --reload"
    
    working_dir: /app
    
    environment:
      - TZ=Europe/Madrid
      - PYTHONUNBUFFERED=1  # Solución para los prints
    
    volumes:
      # Aquí los volúmenes se mapean del servidor real hacia el contenedor
      - /directorio/local/web_aamm_dev:/app

      # MAPEAMOS LOS VÍDEOS
      - /directorio/local/videos:/app/videos_privados

      # Guarda los paquetes de pip en un volumen seguro de Docker
      - cache_pip_dev:/usr/local/lib/python3.10/site-packages
      - cache_bin_dev:/usr/local/bin
    dns:
      - 8.8.8.8
      - 8.8.4.4
    extra_hosts:
      - "host.docker.internal:host-gateway"
    ports:
      - "8891:8888"  
    networks:
      - red_publica

# Declaramos los volúmenes de caché
volumes:
  cache_pip_dev:
  cache_bin_dev:

networks:
  red_publica:
    external: true
```