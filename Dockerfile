# ==============================================================================
# PIPELINE PRODUCTION RUNTIME IMAGE (OPTIMIZED FOR WSL & CLOUD DESKTOPS)
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Configurar variables de entorno para evitar buffers de consola y archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Instalar dependencias esenciales del sistema y limpiar caché de apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Copiar e instalar TODOS los paquetes usando el archivo de requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 3. Copiar la capa de código fuente de la aplicación
COPY src/ ./src/

# Crear la carpeta de persistencia interna
RUN mkdir -p data

# Comando de ejecución nativo: Lanzamos el simulador de telemetría IoT
CMD ["python", "src/simulator.py"]