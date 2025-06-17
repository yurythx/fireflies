#!/bin/bash

# FireFlies - Sistema de Deploy Automatizado
# Detecta automaticamente o ambiente e realiza deploy de forma inteligente

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Função para detectar ambiente
detect_environment() {
    if [[ -n "$ENVIRONMENT" ]]; then
        echo "$ENVIRONMENT"
    elif [[ -n "$HEROKU_APP_NAME" ]] || [[ -n "$DYNO" ]]; then
        echo "production"
    elif [[ -n "$KUBERNETES_SERVICE_HOST" ]]; then
        echo "production"
    elif [[ -n "$DOCKER_CONTAINER" ]]; then
        echo "production"
    elif [[ -n "$STAGING" ]]; then
        echo "staging"
    elif [[ -n "$DEV" ]]; then
        echo "development"
    else
        # Detectar por branch git
        if command -v git &> /dev/null; then
            BRANCH=$(git branch --show-current 2>/dev/null || echo "development")
            case $BRANCH in
                main|master|prod) echo "production" ;;
                staging|stage) echo "staging" ;;
                *) echo "development" ;;
            esac
        else
            echo "development"
        fi
    fi
}

# Função para verificar pré-requisitos
check_prerequisites() {
    log "🔍 Verificando pré-requisitos..."
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log "✅ Python $PYTHON_VERSION encontrado"
    else
        error "❌ Python3 não encontrado"
        return 1
    fi
    
    # Verificar Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log "✅ Docker $DOCKER_VERSION encontrado"
    else
        error "❌ Docker não encontrado"
        return 1
    fi
    
    # Verificar Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        log "✅ Docker Compose $COMPOSE_VERSION encontrado"
    else
        error "❌ Docker Compose não encontrado"
        return 1
    fi
    
    # Verificar Git (opcional)
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        log "✅ Git $GIT_VERSION encontrado"
    else
        warn "⚠️ Git não encontrado (opcional)"
    fi
    
    log "✅ Todos os pré-requisitos atendidos"
    return 0
}

# Função para configurar ambiente
setup_environment() {
    local env=$1
    log "🚀 Configurando ambiente: $env"
    
    # Criar arquivo .env se não existir
    if [[ ! -f .env ]]; then
        log "📝 Criando arquivo .env..."
        cat > .env << EOF
# FireFlies Environment Configuration
ENVIRONMENT=$env
DEBUG=$([[ "$env" == "development" ]] && echo "true" || echo "false")
DJANGO_SETTINGS_MODULE=core.settings$([[ "$env" != "development" ]] && echo "_prod" || echo "_dev")

# Database Configuration
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3
DEBUG_DATABASE=True

# Security
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static Files
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=staticfiles/
MEDIA_ROOT=media/

# Allowed Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
EOF
        log "✅ Arquivo .env criado"
    fi
}

# Função para instalar dependências
install_dependencies() {
    local env=$1
    log "📦 Instalando dependências..."
    
    # Determinar arquivo de requirements
    if [[ "$env" == "production" ]]; then
        requirements_file="requirements-prod.txt"
    else
        requirements_file="requirements.txt"
    fi
    
    if [[ ! -f "$requirements_file" ]]; then
        error "❌ Arquivo $requirements_file não encontrado"
        return 1
    fi
    
    if python3 -m pip install -r "$requirements_file"; then
        log "✅ Dependências instaladas"
        return 0
    else
        error "❌ Falha ao instalar dependências"
        return 1
    fi
}

# Função para executar comandos Django
run_django_commands() {
    local env=$1
    log "🐍 Executando comandos Django..."
    
    # Migrations
    log "🔄 Executando migrations..."
    python3 manage.py migrate
    
    # Collect static (apenas em staging/production)
    if [[ "$env" != "development" ]]; then
        log "📁 Coletando arquivos estáticos..."
        python3 manage.py collectstatic --noinput
    fi
    
    # Inicializar módulos
    log "🔧 Inicializando módulos..."
    python3 manage.py shell -c "
from apps.config.models.app_module_config import AppModuleConfiguration
AppModuleConfiguration.initialize_core_modules()
print('Módulos inicializados com sucesso!')
"
    
    log "✅ Comandos Django executados com sucesso"
}

# Função para build Docker
build_docker() {
    local env=$1
    log "🐳 Construindo imagem Docker..."
    
    # Determinar Dockerfile
    if [[ "$env" == "development" ]]; then
        dockerfile="Dockerfile.dev"
    else
        dockerfile="Dockerfile"
    fi
    
    if [[ ! -f "$dockerfile" ]]; then
        error "❌ Dockerfile $dockerfile não encontrado"
        return 1
    fi
    
    if docker build -f "$dockerfile" -t "fireflies:$env" .; then
        log "✅ Imagem Docker construída"
        return 0
    else
        error "❌ Falha ao construir imagem Docker"
        return 1
    fi
}

# Função para deploy Docker
deploy_docker() {
    local env=$1
    log "🚀 Iniciando deploy com Docker Compose..."
    
    # Determinar arquivo compose
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    else
        compose_file="docker-compose.yml"
    fi
    
    if [[ ! -f "$compose_file" ]]; then
        error "❌ Arquivo $compose_file não encontrado"
        return 1
    fi
    
    # Parar containers existentes
    log "🛑 Parando containers existentes..."
    docker-compose -f "$compose_file" down || true
    
    # Subir novos containers
    log "⬆️ Subindo novos containers..."
    if docker-compose -f "$compose_file" up -d --build; then
        log "✅ Deploy Docker concluído"
        return 0
    else
        error "❌ Falha no deploy Docker"
        return 1
    fi
}

# Função para health check
health_check() {
    log "🏥 Verificando saúde da aplicação..."
    
    # Aguardar aplicação inicializar
    sleep 10
    
    # Tentar acessar health check
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        log "✅ Aplicação está saudável"
        return 0
    else
        error "❌ Falha na verificação de saúde"
        return 1
    fi
}

# Função para limpeza
cleanup() {
    log "🧹 Limpando recursos..."
    
    # Limpar imagens Docker não utilizadas
    docker image prune -f || true
    
    # Limpar containers parados
    docker container prune -f || true
    
    # Limpar volumes não utilizados
    docker volume prune -f || true
    
    log "✅ Limpeza concluída"
}

# Função para encontrar uma porta livre
find_free_port() {
    local port=$1
    while lsof -i :$port >/dev/null 2>&1; do
        port=$((port+1))
    done
    echo $port
}

# Função para atualizar porta no docker-compose.dev.yml
automatizar_porta_compose() {
    local compose_file="docker-compose.dev.yml"
    local default_port=8001
    local container_port=8000
    if [[ ! -f "$compose_file" ]]; then
        error "❌ Arquivo $compose_file não encontrado para automação de porta"
        return 1
    fi
    # Detectar porta livre
    local free_port=$(find_free_port $default_port)
    log "🔌 Usando porta livre $free_port para o serviço web (host)"
    # Atualizar mapeamento de porta no Compose
    sed -i.bak -E "s/\s*- \"[0-9]+:$container_port\"/      - \"$free_port:$container_port\"/g" "$compose_file"
    # Atualizar comando do Django se necessário
    sed -i.bak -E "s/(runserver 0\.0\.0\.)[0-9]+:$container_port/\1$free_port:$container_port/g" "$compose_file"
    # Atualizar .env.dev
    if [[ -f .env.dev ]]; then
        if grep -q "DJANGO_PORT=" .env.dev; then
            sed -i.bak "s/^DJANGO_PORT=.*/DJANGO_PORT=$free_port/" .env.dev
        else
            echo "DJANGO_PORT=$free_port" >> .env.dev
        fi
    fi
    log "✅ docker-compose.dev.yml e .env.dev atualizados para porta $free_port"
}

# Função para atualizar porta no docker-compose.yml (produção)
automatizar_porta_compose_prod() {
    local compose_file="docker-compose.yml"
    local default_port=8000
    local container_port=8000
    if [[ ! -f "$compose_file" ]]; then
        error "❌ Arquivo $compose_file não encontrado para automação de porta (produção)"
        return 1
    fi
    # Detectar porta livre
    local free_port=$(find_free_port $default_port)
    log "🔌 Usando porta livre $free_port para o serviço web (host) [produção]"
    # Atualizar mapeamento de porta no Compose
    sed -i.bak -E "s/\s*- \"[0-9]+:$container_port\"/      - \"$free_port:$container_port\"/g" "$compose_file"
    # Atualizar comando do Django se necessário
    sed -i.bak -E "s/(runserver 0\.0\.0\.0:)[0-9]+/\1$container_port/g" "$compose_file"
    # Atualizar .env
    if [[ -f .env ]]; then
        if grep -q "DJANGO_PORT=" .env; then
            sed -i.bak "s/^DJANGO_PORT=.*/DJANGO_PORT=$free_port/" .env
        else
            echo "DJANGO_PORT=$free_port" >> .env
        fi
    fi
    log "✅ docker-compose.yml e .env atualizados para porta $free_port"
}

# Função para atualizar portas de Nginx e Flower no Compose e .env
automatizar_portas_extras() {
    local compose_file="$1"
    local env_file="$2"
    # Nginx HTTP
    local nginx_http_default=80
    local nginx_https_default=443
    local flower_default=5555
    # Nginx HTTP
    local nginx_http_port=$(find_free_port $nginx_http_default)
    sed -i.bak -E "s/\s*- \"[0-9]+:80\"/      - \"$nginx_http_port:80\"/g" "$compose_file"
    # Nginx HTTPS
    local nginx_https_port=$(find_free_port $nginx_https_default)
    sed -i.bak -E "s/\s*- \"[0-9]+:443\"/      - \"$nginx_https_port:443\"/g" "$compose_file"
    # Flower (se existir)
    if grep -q 'flower:' "$compose_file"; then
        local flower_port=$(find_free_port $flower_default)
        sed -i.bak -E "s/\s*- \"[0-9]+:5555\"/      - \"$flower_port:5555\"/g" "$compose_file"
        if [[ -f "$env_file" ]]; then
            if grep -q "FLOWER_PORT=" "$env_file"; then
                sed -i.bak "s/^FLOWER_PORT=.*/FLOWER_PORT=$flower_port/" "$env_file"
            else
                echo "FLOWER_PORT=$flower_port" >> "$env_file"
            fi
        fi
        log "✅ Porta do Flower atualizada para $flower_port"
    fi
    # Atualizar .env/.env.dev para Nginx
    if [[ -f "$env_file" ]]; then
        if grep -q "NGINX_PORT=" "$env_file"; then
            sed -i.bak "s/^NGINX_PORT=.*/NGINX_PORT=$nginx_http_port/" "$env_file"
        else
            echo "NGINX_PORT=$nginx_http_port" >> "$env_file"
        fi
        if grep -q "NGINX_SSL_PORT=" "$env_file"; then
            sed -i.bak "s/^NGINX_SSL_PORT=.*/NGINX_SSL_PORT=$nginx_https_port/" "$env_file"
        else
            echo "NGINX_SSL_PORT=$nginx_https_port" >> "$env_file"
        fi
    fi
    log "✅ Portas do Nginx atualizadas para $nginx_http_port (HTTP) e $nginx_https_port (HTTPS)"
}

# Função principal de deploy
deploy() {
    local env=$1
    local force=$2
    
    log "🎯 Iniciando deploy do FireFlies..."
    log "📋 Ambiente detectado: $env"
    
    # Verificar pré-requisitos
    if ! check_prerequisites; then
        error "❌ Pré-requisitos não atendidos"
        return 1
    fi
    
    # Setup do ambiente
    if ! setup_environment "$env"; then
        error "❌ Falha no setup do ambiente"
        return 1
    fi
    
    # Instalar dependências
    if ! install_dependencies "$env"; then
        error "❌ Falha na instalação de dependências"
        return 1
    fi
    
    # Comandos Django
    if ! run_django_commands "$env"; then
        error "❌ Falha nos comandos Django"
        return 1
    fi
    
    # Build Docker
    if ! build_docker "$env"; then
        error "❌ Falha no build Docker"
        return 1
    fi
    
    # Chamar automação de porta antes do deploy Docker (dev/prod)
    if [[ "$env" == "development" ]]; then
        automatizar_porta_compose
    elif [[ "$env" == "production" ]]; then
        automatizar_porta_compose_prod
    fi
    
    # Chamar automação de portas extras antes do deploy Docker (dev/prod)
    if [[ "$env" == "development" ]]; then
        automatizar_portas_extras "docker-compose.dev.yml" ".env.dev"
    elif [[ "$env" == "production" ]]; then
        automatizar_portas_extras "docker-compose.yml" ".env"
    fi
    
    # Deploy Docker
    if ! deploy_docker "$env"; then
        error "❌ Falha no deploy Docker"
        return 1
    fi
    
    # Health check
    if ! health_check; then
        if [[ "$force" != "true" ]]; then
            error "❌ Falha na verificação de saúde"
            return 1
        else
            warn "⚠️ Health check falhou, mas continuando (--force)"
        fi
    fi
    
    # Cleanup
    cleanup
    
    log "🎉 Deploy concluído com sucesso!"
    log "🌐 Aplicação disponível em: http://localhost:8000"
    
    # Determinar arquivo compose para logs
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    else
        compose_file="docker-compose.yml"
    fi
    log "📊 Logs: docker-compose -f $compose_file logs -f"
    
    return 0
}

# Função principal
main() {
    local env=""
    local force=false
    local check_only=false
    
    # Parse argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                env="$2"
                shift 2
                ;;
            --force)
                force=true
                shift
                ;;
            --check-only)
                check_only=true
                shift
                ;;
            -h|--help)
                echo "FireFlies Deploy Automatizado"
                echo ""
                echo "Uso: $0 [OPÇÕES]"
                echo ""
                echo "Opções:"
                echo "  --env ENV        Ambiente (development|staging|production)"
                echo "  --force          Forçar deploy mesmo com erros"
                echo "  --check-only     Apenas verificar pré-requisitos"
                echo "  -h, --help       Mostrar esta ajuda"
                echo ""
                echo "Exemplos:"
                echo "  $0                    # Deploy automático"
                echo "  $0 --env production   # Deploy em produção"
                echo "  $0 --check-only       # Verificar pré-requisitos"
                exit 0
                ;;
            *)
                error "Opção desconhecida: $1"
                exit 1
                ;;
        esac
    done
    
    # Detectar ambiente se não especificado
    if [[ -z "$env" ]]; then
        env=$(detect_environment)
    fi
    
    # Verificar se ambiente é válido
    case $env in
        development|staging|production)
            ;;
        *)
            error "Ambiente inválido: $env"
            exit 1
            ;;
    esac
    
    # Executar apenas verificação se solicitado
    if [[ "$check_only" == "true" ]]; then
        check_prerequisites
        exit $?
    fi
    
    # Executar deploy
    deploy "$env" "$force"
    exit $?
}

# Executar função principal
main "$@" 