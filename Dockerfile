# 1. Usamos una imagen base oficial de Python ligera
FROM python:3.10-slim

# 2. Evita que Python escriba archivos .pyc en el disco y fuerza el buffer de salida (para ver los prints)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalamos dependencias del sistema necesarias para compilar ciertas ruedas de Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiamos e instalamos los requerimientos primero (aprovecha la caché de capas de Docker)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. CORREGIDO: Copiamos TODO el contenido de la raíz del proyecto al contenedor
COPY . /app/

# 7. Exponemos el puerto predeterminado
EXPOSE 8888

# 8. Comando por defecto para producción (sin recarga en vivo)
CMD ["sh", "-c", "python /app/database/init_db.py && uvicorn src.main:app --host 0.0.0.0 --port 8888"]