# Biblioteca de Técnicas de Artes Marciales (AAMM)

Aplicación web para la gestión, consulta y visualización de técnicas de artes marciales con soporte multimedia y control de accesos por roles.

## 🌐 Acceso a la Aplicación
La web está desplegada en producción y se puede acceder a través de la siguiente URL:
👉 **[https://aamm.alsdev.com](https://aamm.alsdev.com)**

---

## 🚀 Características Principales

### Para Usuarios y Visitantes
* **Diseño Moderno y Adaptable:** Interfaz Web Responsive que se adapta perfectamente a móviles, tablets y ordenadores.
* **Modo Oscuro Integrado:** Opción para alternar fácilmente entre modo claro y oscuro.
* **Sistema de Autenticación Seguro:** * Registro de usuarios con validación de correo electrónico (envío de email de verificación).
  * Inicio de sesión protegido mediante cookies de seguridad (`HttpOnly`).
  * Gestión de perfil con opción de cambio de contraseña.
* **Buscador Avanzado y Biblioteca:** Consulta del listado completo de técnicas con filtros avanzados, ordenación dinámica y sistema de paginación (*Cargar más*).
* **Fichas de Detalle Multimedia:** Visualización interactiva de cada técnica con su descripción, etiquetas asociadas y reproductor de vídeo integrado.

### Para Administradores (Panel de Gestión)
* **CRUD de Técnicas:** Control total para crear, editar y borrar técnicas de la biblioteca.
* **Gestión de Usuarios:** Panel para activar cuentas, banear, cambiar contraseñas o eliminar usuarios del sistema.
* **Mantenimiento de Taxonomías:** Herramientas para añadir o borrar Disciplinas y Etiquetas.
* **Administración Multimedia:** Control directo para subir vídeos o eliminarlos físicamente del almacenamiento del servidor.

---

## 📁 Estructura del Proyecto

```text
.
├── database/                     # Scripts SQL y lógica de inicialización
│   ├── db_init_config.sql        # Configuración inicial de la Base de Datos
│   ├── init_db.py                # Script Python para ejecutar la migración
│   └── scripts/                  # Migraciones ordenadas por pasos
│       ├── 0001_create_ta_usuarios.sql
│       ├── 0002_insert_ta_usuarios_prueba.sql
│       ├── 0003_create_tablas_tecnicas.sql
│       └── 0004_insert_tablas_tecnicas.sql
├── src/                          # Código fuente de la aplicación (FastAPI)
│   ├── main.py                   # Punto de entrada de la aplicación
│   ├── config.py                 # Gestión de variables de entorno y propiedades
│   ├── models/                   # Modelos de datos de la Base de Datos (SQLAlchemy)
│   │   └── models.py
│   ├── routers/                  # Endpoints de la API y rutas de navegación
│   │   ├── frontEnd.py           # Rutas que sirven las páginas HTML
│   │   ├── login.py              # Lógica de inicio de sesión y cookies
│   │   ├── tecnicas.py           # API endpoints para técnicas
│   │   ├── usuarios.py           # API endpoints para usuarios
│   │   └── videos.py             # API endpoints para la gestión de vídeos
│   ├── schemas/                  # Validadores de datos de entrada/salida (Pydantic)
│   │   ├── autenticacion.py
│   │   └── tecnicas.py
│   ├── static/                   # Archivos estáticos servidos por el navegador
│   │   ├── js/                   # Controladores interactivos de la interfaz
│   │   │   ├── partials/         # Componentes comunes (Navbar)
│   │   │   ├── tecnicas/         # Lógica de buscador, detalle y edición
│   │   │   └── usuarios/         # Lógica de login, registro y administración
│   │   └── videos/               # Almacenamiento local de archivos de vídeo
│   ├── templates/                # Vistas renderizadas en el servidor (Jinja2)
│   │   ├── acerda_de.html        # Presentación del proyecto, de la web
│   │   ├── base.html             # Plantilla madre del sistema
│   │   ├── index.html            # Página de inicio / Biblioteca
│   │   ├── partials/             # Trozos de HTML reutilizables (Navbar, Footer)
│   │   ├── tecnicas/             # Vistas de gestión y detalle de técnicas
│   │   └── usuarios/             # Vistas de login, registro, perfil y admin
│   └── utils/                    # Módulos de utilidad y soporte
│       ├── auth.py               # Encriptación, JWT y seguridad
│       ├── db_tools.py           # Conectores y herramientas de base de datos
│       └── logging_config.py     # Configuración de logs del sistema
├── Dockerfile                    # Configuración de contenedorización del entorno
├── requirements.txt              # Dependencias de librerías de Python
└── notas.txt                     # Apuntes internos de desarrollo
```

---

## 🛠️ Tecnologías Utilizadas
* **Backend**: Python 3.10+, FastAPI (Asíncrono), Uvicorn.
* **Base de Datos**: SQL Server / MySQL (gestionado mediante SQLAlchemy ORM).
* **Seguridad**: Tokens JWT (PyJWT), contraseñas encriptadas con Passlib (bcrypt) y cookies seguras.
* **Frontend**: HTML5, Jinja2 Templates, Tailwind CSS y JavaScript vanilla (ES6+).
* **Despliegue**: Docker, Cloudflare (CDN/Proxy y caché).


---

## 🛠️ YAML para despliegue desde Docker

```YAML
version: '3.8'

services:
  aamm-app:
    build: 
      # Modifica ALSREPO y el token por tus datos reales. Apuntamos a la rama #main
      context: https://github.com/ALSREPO/web_aamm.git#main
      dockerfile: Dockerfile
    container_name: aamm-app
    restart: always
    labels:
      - "com.centurylinklabs.watchtower.enable=false"
    
    # variables
    environment:
      - TZ=Europe/Madrid
      - PYTHONUNBUFFERED=1
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
      # Configuración de inicio de sesión (login)
      - SECRET_KEY=xxxx
      - ALGORITHM=HS256
      - ACCESS_TOKEN_COOKIE_MAX_AGE=2678400 # en segundos, cuanto dura la sesión del usuario, aquí 31 días (31*24*3600 = 2678400)
      - EMAIL_EMISOR=xxxx
      - BASE_URL=xxxx
      # Configuración de servidor de correo
      - SMTP_SERVER=xxxx
      - SMTP_PORT=xxxx
      - SMTP_USERNAME=xxxx
      - SMTP_PASSWORD=xxxx
      # Configuración para el listado de técnicas
      - ORDEN_LISTADO_TECNICAS=fecha
      - NUMERO_TECNICAS_POR_PAGINA=12
      - SENTIDO_ORDEN_LISTADO_TECNICAS=desc
      # Configuración vídeos
      - RUTA_VIDEOS=src/static/videos
      - TAMANYO_MAXIMO_SUBIDA_VIDEOS=300 # en MB

    volumes:
      # MAPEAMOS LOS VÍDEOS
      - /directorio/del/servidor/videos:/app/src/static/videos
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