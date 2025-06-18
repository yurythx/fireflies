#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Função para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Função para verificar se estamos em modo de desenvolvimento
is_development() {
    if [ "${DJANGO_SETTINGS_MODULE:-}" = "core.settings" ] || \
       [ "${DEBUG:-}" = "true" ] || \
       [ "${ENVIRONMENT:-}" = "development" ]; then
        return 0
    else
        return 1
    fi
}

# Função para iniciar servidor de desenvolvimento
start_development_server() {
    log "🚀 Modo de desenvolvimento detectado"
    log "📊 Iniciando servidor Django..."
    
    # Configurações do servidor de desenvolvimento
    local host=${DJANGO_HOST:-0.0.0.0}
    local port=${DJANGO_PORT:-8000}
    
    log "🌐 Servidor disponível em: http://$host:$port"
    
    exec python manage.py runserver "$host:$port"
}

# Função para iniciar servidor de produção
start_production_server() {
    log "🏭 Modo de produção detectado"
    log "📊 Iniciando servidor Gunicorn..."
    
    # Configurações do Gunicorn
    local workers=${GUNICORN_WORKERS:-4}
    local worker_class=${GUNICORN_WORKER_CLASS:-sync}
    local worker_connections=${GUNICORN_WORKER_CONNECTIONS:-1000}
    local max_requests=${GUNICORN_MAX_REQUESTS:-1000}
    local max_requests_jitter=${GUNICORN_MAX_REQUESTS_JITTER:-100}
    local timeout=${GUNICORN_TIMEOUT:-30}
    local keepalive=${GUNICORN_KEEPALIVE:-2}
    local bind=${GUNICORN_BIND:-0.0.0.0:8000}
    local log_level=${GUNICORN_LOG_LEVEL:-info}
    
    # Calcular workers baseado no número de CPUs (se não especificado)
    if [ "$workers" = "auto" ]; then
        workers=$(nproc)
        workers=$((workers * 2 + 1))
        log "🖥️ Workers automáticos calculados: $workers (baseado em $(nproc) CPUs)"
    fi
    
    log "⚙️ Configurações do Gunicorn:"
    log "  📍 Bind: $bind"
    log "  👥 Workers: $workers"
    log "  🔧 Worker Class: $worker_class"
    log "  🔗 Worker Connections: $worker_connections"
    log "  📊 Max Requests: $max_requests"
    log "  ⏱️ Timeout: $timeout"
    log "  📝 Log Level: $log_level"
    
    # Verificar se o Gunicorn está instalado
    if ! command -v gunicorn &> /dev/null; then
        log "❌ Gunicorn não encontrado. Instalando..."
        pip install gunicorn
    fi
    
    # Executar Gunicorn com configurações otimizadas
    exec gunicorn core.wsgi:application \
        --bind "$bind" \
        --workers "$workers" \
        --worker-class "$worker_class" \
        --worker-connections "$worker_connections" \
        --max-requests "$max_requests" \
        --max-requests-jitter "$max_requests_jitter" \
        --timeout "$timeout" \
        --keepalive "$keepalive" \
        --access-logfile - \
        --error-logfile - \
        --log-level "$log_level" \
        --capture-output \
        --enable-stdio-inheritance \
        --preload \
        --chdir /app
}

# Função para verificar saúde da aplicação
health_check() {
    log "🏥 Verificando saúde da aplicação..."
    
    # Aguardar um pouco para a aplicação inicializar
    sleep 5
    
    # Tentar acessar a aplicação
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
            log "✅ Aplicação está saudável"
            return 0
        fi
        
        log "⏳ Tentativa $attempt/$max_attempts - Aguardando aplicação..."
        sleep 3
        attempt=$((attempt + 1))
    done
    
    log "⚠️ Aplicação pode não estar totalmente inicializada"
    return 1
}

# Função principal
main() {
    log "🎯 Iniciando FireFlies..."
    
    # Verificar variáveis de ambiente
    log "📋 Variáveis de ambiente:"
    log "  🏷️ DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-não definido}"
    log "  🐛 DEBUG: ${DEBUG:-não definido}"
    log "  🌍 ENVIRONMENT: ${ENVIRONMENT:-não definido}"
    
    # Verificar se estamos no diretório correto
    if [ ! -f "manage.py" ]; then
        log "❌ manage.py não encontrado. Verifique se está no diretório correto."
        exit 1
    fi
    
    # Verificar se o Django está instalado
    if ! python -c "import django" 2>/dev/null; then
        log "❌ Django não encontrado. Instalando dependências..."
        pip install -r requirements.txt
    fi
    
    # Iniciar servidor baseado no ambiente
    if is_development; then
        start_development_server
    else
        start_production_server
    fi
}

# Executar função principal
main "$@"
