#!/bin/sh
set -e

# Asegurar que PORT tenga un valor por defecto (5000)
export PORT="${PORT:-5000}"

# Si no se configuró SECRET_KEY, generar una temporal para evitar fallo al arrancar
if [ -z "$SECRET_KEY" ]; then
    echo "==> AVISO: SECRET_KEY no fue configurada. Se generó una clave aleatoria temporal para esta sesión."
    echo "==> Para un entorno de producción persistente, configure la variable de entorno SECRET_KEY."
    export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
fi

# Inicializar y verificar esquema de base de datos antes de servir tráfico
echo "==> Inicializando y verificando esquema de base de datos..."
python -c "from app import create_app; create_app()"

# Si no se pasaron argumentos o el primer argumento es 'gunicorn', arrancar servidor WSGI
if [ "$#" -eq 0 ] || [ "$1" = 'gunicorn' ]; then
    # Construir puertos de escucha (escuchar en $PORT y también en 3000/5000 para compatibilidad total)
    BIND_ARGS="--bind 0.0.0.0:${PORT}"
    if [ "${PORT}" != "3000" ]; then
        BIND_ARGS="${BIND_ARGS} --bind 0.0.0.0:3000"
    fi
    if [ "${PORT}" != "5000" ]; then
        BIND_ARGS="${BIND_ARGS} --bind 0.0.0.0:5000"
    fi

    echo "==> Iniciando Gunicorn con ${BIND_ARGS} (workers=${WORKERS:-2}, threads=${THREADS:-4})..."
    exec gunicorn \
        ${BIND_ARGS} \
        --workers "${WORKERS:-2}" \
        --threads "${THREADS:-4}" \
        --worker-class gthread \
        --timeout "${TIMEOUT:-120}" \
        --access-logfile - \
        --error-logfile - \
        "app:app"
fi

# Si se pasó cualquier otro comando (ej: pytest, python run.py, sh, bash)
exec "$@"
