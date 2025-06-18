#!/bin/bash

# FireFlies - Sistema de Deploy Automatizado
# Detecta automaticamente o ambiente e realiza deploy de forma inteligente
# Compatível com Ubuntu, Debian e outras distribuições Linux

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

# Função para detectar IP da máquina
detect_machine_ip() {
    log "🔍 Detectando IP da máquina..."
    
    local ip_addresses=()
    
    # Tentar diferentes métodos de detecção de IP
    if command -v ip &> /dev/null; then
        # Usar comando ip (mais moderno)
        local ip_cmd_result=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' | head -1)
        if [[ -n "$ip_cmd_result" ]]; then
            ip_addresses+=("$ip_cmd_result")
            log "✅ IP detectado via 'ip route': $ip_cmd_result"
        fi
    fi
    
    if command -v hostname &> /dev/null; then
        # Usar hostname -I
        local hostname_result=$(hostname -I 2>/dev/null | awk '{print $1}')
        if [[ -n "$hostname_result" ]]; then
            ip_addresses+=("$hostname_result")
            log "✅ IP detectado via 'hostname -I': $hostname_result"
        fi
    fi
    
    if command -v ifconfig &> /dev/null; then
        # Usar ifconfig (fallback)
        local ifconfig_result=$(ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1)
        if [[ -n "$ifconfig_result" ]]; then
            ip_addresses+=("$ifconfig_result")
            log "✅ IP detectado via 'ifconfig': $ifconfig_result"
        fi
    fi
    
    # Tentar detectar IP via serviços externos (apenas se necessário)
    if [[ ${#ip_addresses[@]} -eq 0 ]]; then
        warn "⚠️ Não foi possível detectar IP local, tentando serviços externos..."
        
        # Tentar diferentes serviços
        local external_services=(
            "ifconfig.me"
            "icanhazip.com"
            "ipinfo.io/ip"
            "ipecho.net/plain"
        )
        
        for service in "${external_services[@]}"; do
            if command -v curl &> /dev/null; then
                local external_ip=$(curl -s --max-time 5 "$service" 2>/dev/null | tr -d '\n\r')
                if [[ -n "$external_ip" ]] && [[ "$external_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                    ip_addresses+=("$external_ip")
                    log "✅ IP externo detectado via $service: $external_ip"
                    break
                fi
            fi
        done
    fi
    
    # Se ainda não encontrou, usar localhost
    if [[ ${#ip_addresses[@]} -eq 0 ]]; then
        warn "⚠️ Não foi possível detectar IP, usando localhost"
        ip_addresses+=("127.0.0.1")
    fi
    
    # Retornar o primeiro IP encontrado
    echo "${ip_addresses[0]}"
}

# Função para detectar hostname da máquina
detect_machine_hostname() {
    log "🏷️ Detectando hostname da máquina..."
    
    local hostname=""
    
    # Tentar diferentes métodos
    if command -v hostname &> /dev/null; then
        hostname=$(hostname 2>/dev/null)
    fi
    
    # Se não encontrou, usar um padrão
    if [[ -z "$hostname" ]]; then
        hostname="fireflies-server"
        warn "⚠️ Hostname não detectado, usando padrão: $hostname"
    fi
    
    echo "$hostname"
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
    
    # Verificar Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log "✅ Docker $DOCKER_VERSION encontrado"
        
        # Verificar se Docker está rodando
        if ! docker info &> /dev/null; then
            error "❌ Docker não está rodando. Inicie o Docker:"
            error "   sudo systemctl start docker"
            error "   sudo usermod -aG docker $USER"
            return 1
        fi
    else
        error "❌ Docker não encontrado. Instale Docker:"
        error "   Ubuntu/Debian: sudo apt install docker.io docker-compose"
        error "   Ou siga: https://docs.docker.com/engine/install/"
        return 1
    fi
    
    # Verificar Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        log "✅ Docker Compose $COMPOSE_VERSION encontrado"
    else
        error "❌ Docker Compose não encontrado. Instale:"
        error "   Ubuntu/Debian: sudo apt install docker-compose"
        error "   Ou: sudo curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose"
        return 1
    fi
    
    # Verificar lsof (para detecção de portas)
    if ! command -v lsof &> /dev/null; then
        warn "⚠️ lsof não encontrado. Instalando..."
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y lsof
        elif command -v yum &> /dev/null; then
            sudo yum install -y lsof
        else
            warn "⚠️ Não foi possível instalar lsof automaticamente"
        fi
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

# Função para criar arquivo .env de forma robusta
create_env_file() {
    local file_path=$1
    local content=$2
    local description=$3
    
    log "📝 Criando $description..."
    
    # Remover arquivo existente se estiver corrompido
    if [[ -f "$file_path" ]]; then
        if ! head -c 1 "$file_path" > /dev/null 2>&1; then
            warn "⚠️ Arquivo $file_path corrompido, removendo..."
            rm -f "$file_path"
        fi
    fi
    
    # Criar arquivo com encoding UTF-8
    if echo -e "$content" > "$file_path"; then
        # Verificar se foi criado corretamente
        if [[ -f "$file_path" ]] && [[ -s "$file_path" ]]; then
            log "✅ $description criado com sucesso"
            return 0
        else
            error "❌ Erro na criação do $description"
            return 1
        fi
    else
        error "❌ Erro ao criar $description"
        return 1
    fi
}

# Função para configurar ambiente
setup_environment() {
    local env=$1
    log "🚀 Configurando ambiente: $env"
    
    # Detectar informações da máquina
    local machine_ip=$(detect_machine_ip)
    local machine_hostname=$(detect_machine_hostname)
    
    log "🌐 IP da máquina detectado: $machine_ip"
    log "🏷️ Hostname detectado: $machine_hostname"
    
    # Criar arquivo .env se não existir
    if [[ ! -f .env ]]; then
        local debug_value=$([[ "$env" == "development" ]] && echo "True" || echo "False")
        local secret_key=$($PYTHON_CMD -c 'import secrets; print(secrets.token_urlsafe(50))')
        
        local env_content="# FireFlies Environment Configuration
ENVIRONMENT=$env
DEBUG=$debug_value
SECRET_KEY=$secret_key

# Machine Information
MACHINE_IP=$machine_ip
MACHINE_HOSTNAME=$machine_hostname

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@fireflies.com

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,170.245.70.68,$machine_ip,$machine_hostname
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://170.245.70.68:8000,http://$machine_ip:8000,http://$machine_hostname:8000

# Static Files
STATIC_URL=/static/
MEDIA_URL=/media/

# Logging
LOG_LEVEL=INFO

# Docker Configuration
DOCKER_COMPOSE_PROJECT_NAME=fireflies
DOCKER_HOST_IP=$machine_ip

# Development Server
DJANGO_HOST=0.0.0.0
DJANGO_PORT=8000"
        
        if ! create_env_file ".env" "$env_content" "arquivo .env"; then
            error "❌ Falha ao criar arquivo .env"
            return 1
        fi
    else
        # Atualizar ALLOWED_HOSTS e CSRF_TRUSTED_ORIGINS se o arquivo já existir
        log "📝 Atualizando configurações de rede no .env existente..."
        
        # Atualizar ALLOWED_HOSTS
        if grep -q "ALLOWED_HOSTS=" .env; then
            # Verificar se o IP já está na lista
            if ! grep -q "$machine_ip" .env; then
                sed -i.bak "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,170.245.70.68,$machine_ip,$machine_hostname/" .env
                log "✅ ALLOWED_HOSTS atualizado com $machine_ip"
            fi
        else
            echo "ALLOWED_HOSTS=localhost,127.0.0.1,170.245.70.68,$machine_ip,$machine_hostname" >> .env
            log "✅ ALLOWED_HOSTS adicionado"
        fi
        
        # Atualizar CSRF_TRUSTED_ORIGINS
        if grep -q "CSRF_TRUSTED_ORIGINS=" .env; then
            # Verificar se o IP já está na lista
            if ! grep -q "$machine_ip" .env; then
                sed -i.bak "s|CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://170.245.70.68:8000,http://$machine_ip:8000,http://$machine_hostname:8000|" .env
                log "✅ CSRF_TRUSTED_ORIGINS atualizado com $machine_ip"
            fi
        else
            echo "CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://170.245.70.68:8000,http://$machine_ip:8000,http://$machine_hostname:8000" >> .env
            log "✅ CSRF_TRUSTED_ORIGINS adicionado"
        fi
        
        # Adicionar informações da máquina se não existirem
        if ! grep -q "MACHINE_IP=" .env; then
            echo "MACHINE_IP=$machine_ip" >> .env
            echo "MACHINE_HOSTNAME=$machine_hostname" >> .env
            log "✅ Informações da máquina adicionadas"
        fi
    fi
    
    # Criar arquivo de primeira instalação se não existir
    if [[ ! -f .first_install ]]; then
        log "📝 Criando arquivo de primeira instalação..."
        touch .first_install
        log "✅ Arquivo .first_install criado"
    fi
    
    # Criar diretórios necessários
    mkdir -p logs media staticfiles
    log "✅ Diretórios criados"
    
    # Mostrar informações de acesso
    log "🌐 Informações de acesso:"
    log "   Local: http://localhost:8000"
    log "   IP Local: http://$machine_ip:8000"
    log "   Hostname: http://$machine_hostname:8000"
    
    return 0
}

# Função para executar comandos Django
run_django_commands() {
    local env=$1
    log "🐍 Executando comandos Django..."
    
    # Migrations
    log "🔄 Executando migrations..."
    $PYTHON_CMD manage.py migrate
    
    # Collect static (apenas em staging/production)
    if [[ "$env" != "development" ]]; then
        log "📁 Coletando arquivos estáticos..."
        $PYTHON_CMD manage.py collectstatic --noinput
    fi
    
    # Verificar se é primeira instalação
    if [[ -f .first_install ]]; then
        log "🎯 Primeira instalação detectada!"
        log "🔧 Inicializando módulos básicos..."
        $PYTHON_CMD manage.py shell -c "
from apps.config.models.app_module_config import AppModuleConfiguration
AppModuleConfiguration.initialize_core_modules()
print('Módulos básicos inicializados com sucesso!')
"
        
        log "✅ Sistema pronto para configuração pós-deploy!"
        log "🌐 Acesse http://localhost:8000/ para configurar o sistema"
    else
        log "🔄 Instalação normal detectada"
        # Inicializar módulos normalmente
        log "🔧 Inicializando módulos..."
        $PYTHON_CMD manage.py shell -c "
from apps.config.models.app_module_config import AppModuleConfiguration
AppModuleConfiguration.initialize_core_modules()
print('Módulos inicializados com sucesso!')
"
    fi
    
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
    
    # Obter IP da máquina para teste
    local machine_ip=$(detect_machine_ip)
    
    # Verificar se é primeira instalação
    if [[ -f .first_install ]]; then
        log "🎯 Primeira instalação detectada - verificando se wizard está acessível..."
        
        # Tentar acessar o wizard de setup em diferentes endereços
        local endpoints=(
            "http://localhost:8000/config/setup/"
            "http://127.0.0.1:8000/config/setup/"
            "http://$machine_ip:8000/config/setup/"
        )
        
        for endpoint in "${endpoints[@]}"; do
            if curl -f "$endpoint" > /dev/null 2>&1; then
                log "✅ Wizard de configuração está acessível em: $endpoint"
                return 0
            fi
        done
        
        error "❌ Wizard de configuração não está acessível"
        return 1
    else
        # Verificação normal de saúde
        local endpoints=(
            "http://localhost:8000/health/"
            "http://127.0.0.1:8000/health/"
            "http://$machine_ip:8000/health/"
        )
        
        for endpoint in "${endpoints[@]}"; do
            if curl -f "$endpoint" > /dev/null 2>&1; then
                log "✅ Aplicação está saudável em: $endpoint"
                return 0
            fi
        done
        
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

# Função para encontrar uma porta livre (compatível com Ubuntu)
find_free_port() {
    local port=$1
    while lsof -i :$port >/dev/null 2>&1; do
        port=$((port+1))
    done
    echo $port
}

# Função para atualizar porta no docker-compose.dev.yml (compatível com Ubuntu)
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
    # Atualizar mapeamento de porta no Compose (compatível com Ubuntu)
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

# Função para atualizar porta no docker-compose.yml (produção) - compatível com Ubuntu
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
    # Atualizar mapeamento de porta no Compose (compatível com Ubuntu)
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

# Função para atualizar portas de Nginx e Flower no Compose e .env (compatível com Ubuntu)
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
    
    # Remover bloco de instalação de dependências Python no host
    # Substituir por mensagem informativa
    log "🐳 Ambiente Docker detectado: dependências Python serão instaladas dentro do container."
    log "📦 Pulando instalação de dependências Python no host."

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
    
    # Obter IP da máquina para exibir informações finais
    local machine_ip=$(detect_machine_ip)
    local machine_hostname=$(detect_machine_hostname)
    
    log "🎉 Deploy concluído com sucesso!"
    log "🌐 Aplicação disponível em:"
    log "   Local: http://localhost:8000"
    log "   IP Local: http://$machine_ip:8000"
    log "   Hostname: http://$machine_hostname:8000"
    
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
                echo ""
                echo "Pré-requisitos Ubuntu/Debian:"
                echo "  sudo apt update"
                echo "  sudo apt install python3 python3-pip python3-venv docker.io docker-compose lsof"
                echo "  sudo usermod -aG docker \$USER"
                echo "  sudo systemctl start docker"
                echo ""
                echo "Funcionalidades:"
                echo "  🔍 Detecção automática de IP da máquina"
                echo "  🌐 Configuração automática de ALLOWED_HOSTS"
                echo "  🔒 Configuração automática de CSRF_TRUSTED_ORIGINS"
                echo "  🚀 Deploy automatizado com Docker"
                echo "  📊 Health checks automáticos"
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