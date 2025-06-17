#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Função para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Iniciando Celery Worker..."

# Configurações do Celery Worker
CONCURRENCY=${CELERY_WORKER_CONCURRENCY:-4}
LOGLEVEL=${CELERY_WORKER_LOGLEVEL:-info}
QUEUES=${CELERY_WORKER_QUEUES:-celery}

log "Configurações do Celery Worker:"
log "  Concurrency: $CONCURRENCY"
log "  Log Level: $LOGLEVEL"
log "  Queues: $QUEUES"

exec celery -A core worker \
    --loglevel=$LOGLEVEL \
    --concurrency=$CONCURRENCY \
    --queues=$QUEUES \
    --without-gossip \
    --without-mingle \
    --without-heartbeat
