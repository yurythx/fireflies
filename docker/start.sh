#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Função para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Iniciando servidor Django..."

# Verificar se estamos em modo de desenvolvimento ou produção
if [ "${DJANGO_SETTINGS_MODULE:-}" = "core.settings" ]; then
    log "Modo de desenvolvimento detectado"
    python manage.py runserver 0.0.0.0:8000
else
    log "Modo de produção detectado"
    
    # Configurações do Gunicorn
    WORKERS=${GUNICORN_WORKERS:-4}
    WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}
    WORKER_CONNECTIONS=${GUNICORN_WORKER_CONNECTIONS:-1000}
    MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-1000}
    MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-100}
    TIMEOUT=${GUNICORN_TIMEOUT:-30}
    KEEPALIVE=${GUNICORN_KEEPALIVE:-2}
    
    log "Configurações do Gunicorn:"
    log "  Workers: $WORKERS"
    log "  Worker Class: $WORKER_CLASS"
    log "  Worker Connections: $WORKER_CONNECTIONS"
    log "  Max Requests: $MAX_REQUESTS"
    log "  Timeout: $TIMEOUT"
    
    exec gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers $WORKERS \
        --worker-class $WORKER_CLASS \
        --worker-connections $WORKER_CONNECTIONS \
        --max-requests $MAX_REQUESTS \
        --max-requests-jitter $MAX_REQUESTS_JITTER \
        --timeout $TIMEOUT \
        --keepalive $KEEPALIVE \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --capture-output \
        --enable-stdio-inheritance
fi
