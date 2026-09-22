#!/bin/sh
set -e

# Si estamos en producción y no se configuró SECRET_KEY, generar una temporal para evitar fallo al arrancar
if [ -z "$SECRET_KEY" ] && [ "${FLASK_ENV}" = "production" ]; then
    echo "==> AVISO: SECRET_KEY no fue configurada. Se generó una clave aleatoria temporal para esta sesión."
    echo "==> Para un entorno de producción persistente, configure la variable de entorno SECRET_KEY."
    export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
fi

# Si el comando es 'gunicorn', inicializar esquema de base de datos y arrancar Gunicorn
if [ "$1" = 'gunicorn' ]; then
    echo "==> Inicializando y verificando esquema de base de datos..."
    python -c "from app import create_app; create_app()"

    echo "==> Iniciando Gunicorn en 0.0.0.0:${PORT:-5000} (workers=${WORKERS:-2}, threads=${THREADS:-4})..."
    exec gunicorn \
        --bind "0.0.0.0:${PORT:-5000}" \
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
