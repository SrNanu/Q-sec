FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema requeridas:
# - build-essential y libpq-dev para módulos C (psutil, psycopg2)
# - libgomp1: runtime OpenMP indispensable para el motor de Qiskit-Aer (C++)
# - curl: utilidades de diagnóstico
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente completo
COPY . .

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    FLASK_ENV=production \
    SECRET_KEY=qsec-production-secure-default-key-3d53c8-dokploy

# Exponer puertos compatibles
EXPOSE 5000 3000

# Arrancar Gunicorn directamente ejecutando create_app() para inicializar la base de datos
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--bind", "0.0.0.0:3000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:create_app()"]
