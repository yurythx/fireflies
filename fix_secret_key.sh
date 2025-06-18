#!/bin/bash

# Script para gerar SECRET_KEY segura para produção
# Corrige o erro: "SECRET_KEY deve ser alterada em produção"

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

# Função para gerar SECRET_KEY segura
generate_secret_key() {
    # Gerar SECRET_KEY usando openssl
    openssl rand -base64 50 | tr -d "=+/" | cut -c1-50
}

main() {
    log_info "🔐 Gerando SECRET_KEY segura para produção"
    log_info "=========================================="
    
    # Verificar se arquivo .env existe
    if [[ ! -f .env ]]; then
        log_error "Arquivo .env não encontrado"
        log_info "Execute primeiro: ./fix_deploy_issues.sh"
        exit 1
    fi
    
    # Fazer backup do .env
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    log_info "Backup criado: .env.backup.*"
    
    # Gerar nova SECRET_KEY
    log_info "Gerando nova SECRET_KEY..."
    new_secret_key=$(generate_secret_key)
    
    # Verificar se a SECRET_KEY atual é a padrão
    current_secret_key=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2-)
    
    if [[ "$current_secret_key" == *"django-insecure-change-this-in-production"* ]] || \
       [[ "$current_secret_key" == *"your-secret-key-change-this-in-production"* ]]; then
        log_warning "SECRET_KEY atual é a padrão, alterando..."
        
        # Substituir a SECRET_KEY
        sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$new_secret_key|" .env
        
        log_success "SECRET_KEY alterada para produção"
        log_info "Nova SECRET_KEY: $new_secret_key"
    else
        log_warning "SECRET_KEY já foi alterada"
        log_info "SECRET_KEY atual: ${current_secret_key:0:20}..."
    fi
    
    # Verificar outras configurações de segurança
    log_info ""
    log_info "Verificando configurações de segurança..."
    
    # Verificar DEBUG
    if grep -q "^DEBUG=True" .env; then
        log_warning "DEBUG está True, alterando para False..."
        sed -i "s|^DEBUG=True|DEBUG=False|" .env
        log_success "DEBUG alterado para False"
    else
        log_success "DEBUG já está False"
    fi
    
    # Verificar ALLOWED_HOSTS
    if ! grep -q "192.168.1.100" .env; then
        log_warning "IP do servidor não está em ALLOWED_HOSTS, adicionando..."
        sed -i "s|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100|" .env
        log_success "IP 192.168.1.100 adicionado ao ALLOWED_HOSTS"
    else
        log_success "IP do servidor já está em ALLOWED_HOSTS"
    fi
    
    # Verificar CSRF_TRUSTED_ORIGINS
    if ! grep -q "192.168.1.100" .env || ! grep -q "^CSRF_TRUSTED_ORIGINS=" .env; then
        log_warning "Configurando CSRF_TRUSTED_ORIGINS..."
        if grep -q "^CSRF_TRUSTED_ORIGINS=" .env; then
            sed -i "s|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://192.168.1.100|" .env
        else
            echo "CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://192.168.1.100" >> .env
        fi
        log_success "CSRF_TRUSTED_ORIGINS configurado"
    else
        log_success "CSRF_TRUSTED_ORIGINS já está configurado"
    fi
    
    log_info ""
    log_info "✅ Configurações de segurança aplicadas!"
    log_info ""
    log_info "📋 Próximos passos:"
    log_info "1. Execute: ./deploy_improved.sh --check-only"
    log_info "2. Se OK, execute: ./deploy_improved.sh"
    log_info ""
    log_info "🔍 Para verificar:"
    log_info "  grep '^SECRET_KEY=' .env"
    log_info "  grep '^DEBUG=' .env"
}

main "$@" 