# ==============================================================================
# PIPELINE PRODUCTION RUNTIME IMAGE (OPTIMIZED FOR WSL & CLOUD DESKTOPS)
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# 1. Instalar dependencias esenciales del sistema y limpiar caché de apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Copiar e instalar los paquetes de Python directamente en el entorno aislado
COPY requirements.txt .
RUN pip install --no-cache-dir polars==1.0.0

# 3. Copiar la capa de código fuente de la aplicación
COPY src/ ./src/

# Configurar variables de entorno para evitar buffers de consola
ENV PYTHONUNBUFFERED=1

# Crear la carpeta de persistencia interna
RUN mkdir -p data

# Comando de ejecución nativo del pipeline logístico
CMD ["python", "src/pipeline.py"]