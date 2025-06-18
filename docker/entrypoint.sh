#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Função para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Função para aguardar serviços (compatível com Ubuntu)
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=${4:-30}
    local attempt=1
    
    log "Aguardando $service_name em $host:$port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            log "$service_name está disponível!"
            return 0
        fi
        
        log "Tentativa $attempt/$max_attempts - $service_name ainda não está disponível..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log "ERRO: $service_name não ficou disponível após $max_attempts tentativas"
    return 1
}

# Função para verificar se o banco de dados está configurado
check_database_config() {
    if [ -n "${DATABASE_URL:-}" ]; then
        return 0
    elif [ -n "${DB_HOST:-}" ] && [ "${DB_HOST}" != "localhost" ]; then
        return 0
    elif [ -n "${DB_ENGINE:-}" ] && [ "$DB_ENGINE" != "sqlite" ]; then
        return 0
    else
        return 1
    fi
}

# Função para verificar se o Redis está configurado
check_redis_config() {
    if [ -n "${REDIS_URL:-}" ]; then
        return 0
    elif [ -n "${REDIS_HOST:-}" ]; then
        return 0
    else
        return 1
    fi
}

# Função para executar migrations com retry
run_migrations() {
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Executando migrations (tentativa $attempt/$max_attempts)..."
        
        if python manage.py migrate --noinput; then
            log "✅ Migrations executadas com sucesso"
            return 0
        else
            log "⚠️ Falha na tentativa $attempt de migrations"
            if [ $attempt -eq $max_attempts ]; then
                log "❌ Falha definitiva nas migrations"
                return 1
            fi
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
}

# Função para coletar arquivos estáticos
collect_static() {
    log "Coletando arquivos estáticos..."
    
    if python manage.py collectstatic --noinput --clear; then
        log "✅ Arquivos estáticos coletados com sucesso"
        return 0
    else
        log "⚠️ Falha ao coletar arquivos estáticos"
        return 1
    fi
}

# Função para criar superusuário
create_superuser() {
    log "Verificando superusuário..."
    
    python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    try:
        User.objects.create_superuser(
            username='admin',
            email='admin@fireflies.com',
            password='admin123',
            first_name='Admin',
            last_name='System'
        )
        print("✅ Superusuário criado: admin/admin123")
    except Exception as e:
        print(f"⚠️ Erro ao criar superusuário: {e}")
else:
    print("ℹ️ Superusuário já existe")
EOF
}

# Verificar se é primeira instalação
if [ -f "/app/.first_install" ]; then
    log "🎯 Primeira instalação detectada - pulando configuração automática"
    log "🔧 Use o wizard de configuração em http://localhost:8000/"
    
    # Aguardar banco de dados apenas se configurado
    if check_database_config; then
        DB_HOST=${DB_HOST:-localhost}
        DB_PORT=${DB_PORT:-5432}
        wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL" 10
    fi
    
    # Aguardar Redis apenas se configurado
    if check_redis_config; then
        if [ -n "${REDIS_URL:-}" ]; then
            REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/.*:\/\/\([^:]*\).*/\1/p')
            REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\).*/\1/p')
        else
            REDIS_HOST=${REDIS_HOST:-localhost}
            REDIS_PORT=${REDIS_PORT:-6379}
        fi
        
        if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
            wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis" 10
        fi
    fi
    
    # Executar apenas migrations básicas para primeira instalação
    run_migrations || log "⚠️ Migrations podem falhar em primeira instalação"
    
    # NÃO coletar arquivos estáticos em primeira instalação
    # NÃO criar superusuário em primeira instalação
    
else
    log "🔄 Instalação normal detectada"
    
    # Aguardar banco de dados
    if check_database_config; then
        DB_HOST=${DB_HOST:-localhost}
        DB_PORT=${DB_PORT:-5432}
        wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"
    fi
    
    # Aguardar Redis
    if check_redis_config; then
        if [ -n "${REDIS_URL:-}" ]; then
            REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/.*:\/\/\([^:]*\).*/\1/p')
            REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\).*/\1/p')
        else
            REDIS_HOST=${REDIS_HOST:-localhost}
            REDIS_PORT=${REDIS_PORT:-6379}
        fi
        
        if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
            wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
        fi
    fi
    
    # Executar migrações
    run_migrations
    
    # Coletar arquivos estáticos
    collect_static
    
    # Criar superusuário apenas se não existir (backup)
    create_superuser
fi

# Verificar se o comando foi passado
if [ $# -eq 0 ]; then
    log "❌ Nenhum comando especificado"
    exit 1
fi

# Executar comando passado como argumento
log "Executando comando: $*"
exec "$@"
