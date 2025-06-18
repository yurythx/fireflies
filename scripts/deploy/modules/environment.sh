#!/bin/bash

# Módulo de Ambiente - FireFlies Deploy
# Gerencia detecção e configuração de ambiente

# Detectar ambiente automaticamente
detect_environment() {
    if [[ -n "${ENVIRONMENT:-}" ]]; then
        echo "${ENVIRONMENT,,}"  # lowercase
    elif [[ -n "${HEROKU_APP_NAME:-}" ]] || [[ -n "${DYNO:-}" ]]; then
        echo "production"
    elif [[ -n "${KUBERNETES_SERVICE_HOST:-}" ]]; then
        echo "production"
    elif [[ -n "${DOCKER_CONTAINER:-}" ]]; then
        echo "production"
    elif [[ -n "${STAGING:-}" ]]; then
        echo "staging"
    elif [[ -n "${DEV:-}" ]]; then
        echo "development"
    else
        # Detectar por branch git
        if command -v git &> /dev/null; then
            local branch
            branch=$(git branch --show-current 2>/dev/null || echo "development")
            case $branch in
                main|master|prod) echo "production" ;;
                staging|stage) echo "staging" ;;
                *) echo "development" ;;
            esac
        else
            echo "development"
        fi
    fi
}

# Validar ambiente
is_valid_environment() {
    local env="$1"
    case $env in
        development|staging|production)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Detectar IP da máquina
detect_machine_ip() {
    log_info "Detectando IP da máquina..."
    
    local ip_addresses=()
    
    # Método 1: ip route (moderno)
    if command -v ip &> /dev/null; then
        local ip_cmd_result
        ip_cmd_result=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' | head -1)
        if [[ -n "$ip_cmd_result" ]]; then
            ip_addresses+=("$ip_cmd_result")
            log_success "IP detectado via 'ip route': $ip_cmd_result"
        fi
    fi
    
    # Método 2: hostname -I
    if command -v hostname &> /dev/null; then
        local hostname_result
        hostname_result=$(hostname -I 2>/dev/null | awk '{print $1}')
        if [[ -n "$hostname_result" ]]; then
            ip_addresses+=("$hostname_result")
            log_success "IP detectado via 'hostname -I': $hostname_result"
        fi
    fi
    
    # Método 3: ifconfig (fallback)
    if command -v ifconfig &> /dev/null; then
        local ifconfig_result
        ifconfig_result=$(ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1)
        if [[ -n "$ifconfig_result" ]]; then
            ip_addresses+=("$ifconfig_result")
            log_success "IP detectado via 'ifconfig': $ifconfig_result"
        fi
    fi
    
    # Método 4: Serviços externos (último recurso)
    if [[ ${#ip_addresses[@]} -eq 0 ]]; then
        log_warning "Não foi possível detectar IP local, tentando serviços externos..."
        
        local external_services=(
            "ifconfig.me"
            "icanhazip.com"
            "ipinfo.io/ip"
            "ipecho.net/plain"
        )
        
        for service in "${external_services[@]}"; do
            if command -v curl &> /dev/null; then
                local external_ip
                external_ip=$(curl -s --max-time 5 "$service" 2>/dev/null | tr -d '\n\r')
                if [[ -n "$external_ip" ]] && [[ "$external_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                    ip_addresses+=("$external_ip")
                    log_success "IP externo detectado via $service: $external_ip"
                    break
                fi
            fi
        done
    fi
    
    # Fallback para localhost
    if [[ ${#ip_addresses[@]} -eq 0 ]]; then
        log_warning "Não foi possível detectar IP, usando localhost"
        ip_addresses+=("127.0.0.1")
    fi
    
    echo "${ip_addresses[0]}"
}

# Detectar hostname da máquina
detect_machine_hostname() {
    log_info "Detectando hostname da máquina..."
    
    local hostname=""
    
    if command -v hostname &> /dev/null; then
        hostname=$(hostname 2>/dev/null)
    fi
    
    if [[ -z "$hostname" ]]; then
        hostname="fireflies-server"
        log_warning "Hostname não detectado, usando padrão: $hostname"
    fi
    
    echo "$hostname"
}

# Setup do ambiente
setup_environment() {
    local env="$1"
    log_info "Configurando ambiente: $env"
    
    # Detectar informações da máquina
    local machine_ip
    machine_ip=$(detect_machine_ip)
    local machine_hostname
    machine_hostname=$(detect_machine_hostname)
    
    log_info "IP da máquina: $machine_ip"
    log_info "Hostname: $machine_hostname"
    
    # Criar arquivo .env se não existir
    if [[ ! -f .env ]]; then
        create_env_file "$env" "$machine_ip" "$machine_hostname"
    else
        update_env_file "$machine_ip" "$machine_hostname"
    fi
    
    # Criar diretórios necessários
    mkdir -p logs media staticfiles backups
    
    # Criar arquivo de primeira instalação se não existir
    if [[ ! -f .first_install ]]; then
        touch .first_install
        log_success "Arquivo .first_install criado"
    fi
    
    return 0
}

# Criar arquivo .env
create_env_file() {
    local env="$1"
    local machine_ip="$2"
    local machine_hostname="$3"
    
    local debug_value
    debug_value=$([[ "$env" == "development" ]] && echo "True" || echo "False")
    
    local secret_key
    secret_key=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null || echo "django-insecure-development-key-change-in-production")
    
    cat > .env << EOF
# FireFlies Environment Configuration
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
ALLOWED_HOSTS=localhost,127.0.0.1,$machine_ip,$machine_hostname
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://$machine_ip:8000,http://$machine_hostname:8000

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
DJANGO_PORT=8000
EOF
    
    log_success "Arquivo .env criado"
}

# Atualizar arquivo .env existente
update_env_file() {
    local machine_ip="$1"
    local machine_hostname="$2"
    
    log_info "Atualizando configurações de rede no .env existente..."
    
    # Atualizar ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS=" .env; then
        if ! grep -q "$machine_ip" .env; then
            sed -i.bak "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,$machine_ip,$machine_hostname/" .env
            log_success "ALLOWED_HOSTS atualizado com $machine_ip"
        fi
    else
        echo "ALLOWED_HOSTS=localhost,127.0.0.1,$machine_ip,$machine_hostname" >> .env
        log_success "ALLOWED_HOSTS adicionado"
    fi
    
    # Atualizar CSRF_TRUSTED_ORIGINS
    if grep -q "CSRF_TRUSTED_ORIGINS=" .env; then
        if ! grep -q "$machine_ip" .env; then
            sed -i.bak "s|CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://$machine_ip:8000,http://$machine_hostname:8000|" .env
            log_success "CSRF_TRUSTED_ORIGINS atualizado com $machine_ip"
        fi
    else
        echo "CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://$machine_ip:8000,http://$machine_hostname:8000" >> .env
        log_success "CSRF_TRUSTED_ORIGINS adicionado"
    fi
    
    # Adicionar informações da máquina se não existirem
    if ! grep -q "MACHINE_IP=" .env; then
        echo "MACHINE_IP=$machine_ip" >> .env
        echo "MACHINE_HOSTNAME=$machine_hostname" >> .env
        log_success "Informações da máquina adicionadas"
    fi
}

# Mostrar informações de acesso
show_access_info() {
    local env="$1"
    local machine_ip
    machine_ip=$(detect_machine_ip)
    local machine_hostname
    machine_hostname=$(detect_machine_hostname)
    
    log_success "Deploy concluído com sucesso!"
    log_info "Aplicação disponível em:"
    log_info "  Local: http://localhost:8000"
    log_info "  IP Local: http://$machine_ip:8000"
    log_info "  Hostname: http://$machine_hostname:8000"
    
    # Determinar arquivo compose para logs
    local compose_file
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    else
        compose_file="docker-compose.yml"
    fi
    log_info "Logs: docker-compose -f $compose_file logs -f"
} 