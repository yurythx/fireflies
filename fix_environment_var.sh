#!/bin/bash

# Script para adicionar variável ENVIRONMENT ausente
# Corrige o erro: "Variáveis obrigatórias ausentes: ENVIRONMENT"

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

main() {
    log_info "🔧 Adicionando variável ENVIRONMENT ao .env"
    log_info "========================================="
    
    # Verificar se arquivo .env existe
    if [[ ! -f .env ]]; then
        log_error "Arquivo .env não encontrado"
        log_info "Execute primeiro: ./fix_deploy_issues.sh"
        exit 1
    fi
    
    # Verificar se ENVIRONMENT já existe
    if grep -q "^ENVIRONMENT=" .env; then
        log_warning "Variável ENVIRONMENT já existe no .env"
        log_info "Valor atual:"
        grep "^ENVIRONMENT=" .env
    else
        log_info "Adicionando variável ENVIRONMENT..."
        
        # Fazer backup do .env
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        log_info "Backup criado: .env.backup.*"
        
        # Adicionar ENVIRONMENT no início do arquivo
        echo "ENVIRONMENT=production" > .env.temp
        cat .env >> .env.temp
        mv .env.temp .env
        
        log_success "Variável ENVIRONMENT=production adicionada"
    fi
    
    # Verificar se há outras variáveis obrigatórias ausentes
    log_info ""
    log_info "Verificando outras variáveis obrigatórias..."
    
    # Lista de variáveis que devem estar presentes
    required_vars=(
        "DEBUG"
        "SECRET_KEY"
        "ALLOWED_HOSTS"
        "DB_NAME"
        "DB_USER"
        "DB_PASSWORD"
        "DB_HOST"
        "DB_PORT"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_warning "Variáveis ausentes: ${missing_vars[*]}"
        log_info "Adicionando variáveis ausentes..."
        
        for var in "${missing_vars[@]}"; do
            case $var in
                "DEBUG")
                    echo "DEBUG=False" >> .env
                    ;;
                "SECRET_KEY")
                    echo "SECRET_KEY=django-insecure-$(openssl rand -hex 32)" >> .env
                    ;;
                "ALLOWED_HOSTS")
                    echo "ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100" >> .env
                    ;;
                "DB_NAME")
                    echo "DB_NAME=fireflies_prod" >> .env
                    ;;
                "DB_USER")
                    echo "DB_USER=fireflies_user" >> .env
                    ;;
                "DB_PASSWORD")
                    echo "DB_PASSWORD=fireflies_password" >> .env
                    ;;
                "DB_HOST")
                    echo "DB_HOST=db" >> .env
                    ;;
                "DB_PORT")
                    echo "DB_PORT=5432" >> .env
                    ;;
            esac
            log_success "Adicionada: $var"
        done
    else
        log_success "Todas as variáveis obrigatórias estão presentes"
    fi
    
    log_info ""
    log_info "✅ Correção concluída!"
    log_info ""
    log_info "📋 Próximos passos:"
    log_info "1. Execute: ./deploy_improved.sh --check-only"
    log_info "2. Se OK, execute: ./deploy_improved.sh"
    log_info ""
    log_info "🔍 Para verificar:"
    log_info "  cat .env | grep ENVIRONMENT"
}

main "$@" 