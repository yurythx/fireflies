#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Função para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Função para aguardar serviços
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    log "Aguardando $service_name em $host:$port..."
    
    while ! nc -z "$host" "$port"; do
        log "Aguardando $service_name..."
        sleep 1
    done
    
    log "$service_name está disponível!"
}

# Verificar se é primeira instalação
if [ -f "/app/.first_install" ]; then
    log "🎯 Primeira instalação detectada - pulando configuração automática"
    log "🔧 Use o wizard de configuração em http://localhost:8000/"
    
    # Aguardar banco de dados apenas se configurado
    if [ -n "${DB_HOST:-}" ] && [ "${DB_HOST}" != "localhost" ]; then
        wait_for_service "$DB_HOST" "${DB_PORT:-5432}" "PostgreSQL"
    fi
    
    # Aguardar Redis apenas se configurado
    if [ -n "${REDIS_URL:-}" ]; then
        REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/.*:\/\/\([^:]*\).*/\1/p')
        REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\).*/\1/p')
        if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
            wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
        fi
    fi
    
    # Executar apenas migrations básicas para primeira instalação
    log "Executando migrations básicas..."
    python manage.py migrate --noinput || log "⚠️ Migrations podem falhar em primeira instalação"
    
    # NÃO coletar arquivos estáticos em primeira instalação
    # NÃO criar superusuário em primeira instalação
    
else
    log "🔄 Instalação normal detectada"
    
    # Aguardar banco de dados
    if [ -n "${DB_HOST:-}" ]; then
        wait_for_service "$DB_HOST" "${DB_PORT:-5432}" "PostgreSQL"
    fi
    
    # Aguardar Redis
    if [ -n "${REDIS_URL:-}" ]; then
        REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/.*:\/\/\([^:]*\).*/\1/p')
        REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\).*/\1/p')
        if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
            wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
        fi
    fi
    
    # Executar migrações
    log "Executando migrações do banco de dados..."
    python manage.py migrate --noinput
    
    # Coletar arquivos estáticos
    log "Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput --clear
    
    # Criar superusuário apenas se não existir (backup)
    log "Verificando superusuário..."
    python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@havoc.com',
        password='admin123',
        first_name='Admin',
        last_name='System'
    )
    print("Superusuário criado: admin/admin123")
else:
    print("Superusuário já existe")
EOF
fi

# Executar comando passado como argumento
log "Executando comando: $*"
exec "$@"
