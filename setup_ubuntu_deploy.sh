#!/bin/bash

# Script de Configuração para Deploy Ubuntu - FireFlies
# Corrige problemas identificados no deploy

set -euo pipefail

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Função de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função principal
main() {
    log_info "🔧 Configurando ambiente Ubuntu para deploy FireFlies"
    log_info "====================================================="
    
    # 1. Instalar Docker Compose
    log_info ""
    log_info "1. Instalando Docker Compose..."
    if ! command_exists docker-compose; then
        log_info "Instalando Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        log_success "Docker Compose instalado"
    else
        log_success "Docker Compose já está instalado"
    fi
    
    # 2. Adicionar usuário ao grupo docker
    log_info ""
    log_info "2. Configurando permissões Docker..."
    if ! groups $USER | grep -q docker; then
        log_info "Adicionando usuário ao grupo docker..."
        sudo usermod -aG docker $USER
        log_warning "Usuário adicionado ao grupo docker"
        log_warning "Reinicie a sessão ou execute: newgrp docker"
    else
        log_success "Usuário já está no grupo docker"
    fi
    
    # 3. Criar arquivo .env
    log_info ""
    log_info "3. Criando arquivo .env..."
    if [[ ! -f .env ]]; then
        cat > .env << 'EOF'
# Configurações do Django
DEBUG=False
SECRET_KEY=django-insecure-change-this-in-production-$(openssl rand -hex 32)
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100

# Configurações do Banco de Dados
DB_NAME=fireflies_prod
DB_USER=fireflies_user
DB_PASSWORD=fireflies_password
DB_HOST=db
DB_PORT=5432

# Configurações de Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Configurações do Redis
REDIS_URL=redis://redis:6379/0

# Configurações de Log
LOG_LEVEL=INFO
LOG_FILE=/app/logs/fireflies.log

# Configurações de Segurança
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://192.168.1.100
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Configurações de Timezone
TIME_ZONE=America/Sao_Paulo
USE_TZ=True

# Configurações de Idioma
LANGUAGE_CODE=pt-br
USE_I18N=True
USE_L10N=True

# Configurações de Arquivos Estáticos
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/media

# Configurações de Cache
CACHE_BACKEND=django_redis.cache.RedisCache
CACHE_LOCATION=redis://redis:6379/1

# Configurações de Sessão
SESSION_ENGINE=django.contrib.sessions.backends.cache
SESSION_CACHE_ALIAS=default

# Configurações de Upload
FILE_UPLOAD_MAX_MEMORY_SIZE=2621440
DATA_UPLOAD_MAX_MEMORY_SIZE=2621440

# Configurações de Logging
LOGGING_CONFIG=
DJANGO_LOG_LEVEL=INFO
EOF
        log_success "Arquivo .env criado"
    else
        log_success "Arquivo .env já existe"
    fi
    
    # 4. Verificar e corrigir docker-compose.yml
    log_info ""
    log_info "4. Validando docker-compose.yml..."
    if command_exists docker-compose; then
        if docker-compose config >/dev/null 2>&1; then
            log_success "docker-compose.yml está válido"
        else
            log_error "docker-compose.yml tem erros de sintaxe"
            log_info "Verificando sintaxe..."
            docker-compose config
            exit 1
        fi
    fi
    
    # 5. Verificar portas ocupadas
    log_info ""
    log_info "5. Verificando portas..."
    if netstat -tuln | grep -q ":80 "; then
        log_warning "Porta 80 está ocupada"
        log_info "Serviços usando porta 80:"
        sudo netstat -tulpn | grep :80
    else
        log_success "Porta 80 está livre"
    fi
    
    if netstat -tuln | grep -q ":8000 "; then
        log_warning "Porta 8000 está ocupada"
        log_info "Serviços usando porta 8000:"
        sudo netstat -tulpn | grep :8000
    else
        log_success "Porta 8000 está livre"
    fi
    
    # 6. Criar diretórios necessários
    log_info ""
    log_info "6. Criando diretórios necessários..."
    mkdir -p logs
    mkdir -p staticfiles
    mkdir -p media
    log_success "Diretórios criados"
    
    # 7. Configurar permissões
    log_info ""
    log_info "7. Configurando permissões..."
    chmod +x deploy_improved.sh
    chmod +x setup_ubuntu_deploy.sh
    log_success "Permissões configuradas"
    
    log_info ""
    log_info "✅ Configuração concluída!"
    log_info ""
    log_info "📋 Próximos passos:"
    log_info "1. Reinicie a sessão ou execute: newgrp docker"
    log_info "2. Edite o arquivo .env com suas configurações"
    log_info "3. Execute: ./deploy_improved.sh"
    log_info ""
    log_info "🔧 Comandos úteis:"
    log_info "  ./deploy_improved.sh --check-only    # Verificar pré-requisitos"
    log_info "  ./deploy_improved.sh --health        # Verificar saúde dos containers"
    log_info "  ./deploy_improved.sh --logs          # Ver logs"
}

# Execução
main "$@" 