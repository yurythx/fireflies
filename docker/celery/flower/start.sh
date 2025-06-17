#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Função para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Iniciando Flower..."

# Configurações do Flower
PORT=${FLOWER_PORT:-5555}
BASIC_AUTH=${FLOWER_BASIC_AUTH:-}

log "Configurações do Flower:"
log "  Port: $PORT"

if [ -n "$BASIC_AUTH" ]; then
    log "  Basic Auth: Habilitado"
    exec celery -A core flower \
        --port=$PORT \
        --basic_auth=$BASIC_AUTH
else
    log "  Basic Auth: Desabilitado"
    exec celery -A core flower \
        --port=$PORT
fi
