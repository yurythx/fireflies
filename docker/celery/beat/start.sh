#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Função para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Iniciando Celery Beat..."

# Remover arquivo de PID se existir
rm -f /tmp/celerybeat.pid

# Configurações do Celery Beat
LOGLEVEL=${CELERY_BEAT_LOGLEVEL:-info}

log "Configurações do Celery Beat:"
log "  Log Level: $LOGLEVEL"

exec celery -A core beat \
    --loglevel=$LOGLEVEL \
    --pidfile=/tmp/celerybeat.pid
