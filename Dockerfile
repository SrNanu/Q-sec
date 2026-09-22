# =========================================================================
# Etapa 1: Builder (Compilación de librerías nativas y virtualenv)
# =========================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Paquetes requeridos para compilar dependencias con componentes C/C++
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear entorno virtual aislado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# =========================================================================
# Etapa 2: Runtime (Imagen final liviana y segura para producción)
# =========================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Dependencias mínimas de sistema en ejecución (curl para healthcheck, libpq5 para postgresql)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual optimizado desde la etapa builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Variables de entorno estándar
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    FLASK_ENV=production

# Crear usuario y grupo de sistema sin privilegios root
RUN groupadd -r qsec && useradd -r -g qsec -d /app -s /sbin/nologin qsec

# Crear carpetas necesarias y asignar propiedad al usuario qsec
RUN mkdir -p /app/instance && \
    chown -R qsec:qsec /app

# Copiar el código de la aplicación
COPY --chown=qsec:qsec . .

# Normalizar saltos de línea y asignar permisos de ejecución al entrypoint
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Cambiar a usuario no root por seguridad
USER qsec

# Exponer el puerto por defecto
EXPOSE 5000

# Verificación de salud (Healthcheck)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/ || exit 1

# Entrypoint y comando por defecto
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn"]
