#!/bin/bash

# FireFlies - Sistema de Deploy Automatizado Melhorado
# Versão modular e otimizada

set -euo pipefail  # Fail fast, fail safe

# Importar módulos
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/deploy/modules/logging.sh"
source "$SCRIPT_DIR/scripts/deploy/modules/environment.sh"
source "$SCRIPT_DIR/scripts/deploy/modules/validation.sh"
source "$SCRIPT_DIR/scripts/deploy/modules/docker.sh"
source "$SCRIPT_DIR/scripts/deploy/modules/health.sh"

# Configurações
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly LOG_FILE="${PROJECT_ROOT}/logs/deploy_$(date +%Y%m%d_%H%M%S).log"
readonly CONFIG_FILE="${PROJECT_ROOT}/deploy.config"

# Variáveis globais
ENVIRONMENT=""
SKIP_VALIDATION=false
SKIP_HEALTH_CHECK=false
FORCE_DEPLOY=false
BACKUP_BEFORE_DEPLOY=true
CLEANUP_AFTER_DEPLOY=false
MONITOR_MODE=false

# Garantir que o .env existe e a SECRET_KEY é segura
ensure_env_and_secret_key() {
    log_info "Verificando configuração do .env e SECRET_KEY..."
    
    # Detectar IP do servidor
    local server_ip
    server_ip=$(hostname -I | awk '{print $1}' | head -1)
    if [[ -z "$server_ip" ]]; then
        server_ip="192.168.1.100"  # Fallback
    fi
    
    # Detectar hostname
    local server_hostname
    server_hostname=$(hostname)
    
    log_info "IP do servidor detectado: $server_ip"
    log_info "Hostname detectado: $server_hostname"
    
    if [[ ! -f .env ]]; then
        log_info "Criando arquivo .env padrão..."
        
        # Gerar SECRET_KEY segura
        local secret_key
        secret_key=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
        
        # Criar .env básico com configurações otimizadas
        cat > .env << EOF
# Configuração do Ambiente
ENVIRONMENT=production

# Configurações do Django
DEBUG=False
SECRET_KEY=$secret_key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,$server_ip,$server_hostname

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
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://0.0.0.0:8000,http://$server_ip:8000,http://$server_hostname:8000
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

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

# Configurações de CORS (para desenvolvimento)
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://$server_ip:8000
CORS_ALLOW_CREDENTIALS=True
EOF
        
        log_success "Arquivo .env criado com SECRET_KEY segura e configurações de rede otimizadas"
        return 0
    else
        log_info "Arquivo .env já existe, verificando SECRET_KEY e configurações de rede..."
        
        # Verificar se SECRET_KEY é insegura
        if grep -q "django-insecure-change-this-in-production" .env; then
            log_warning "SECRET_KEY insegura detectada, corrigindo..."
            
            # Fazer backup do .env
            cp .env ".env.backup.$(date +%Y%m%d_%H%M%S)"
            
            # Gerar nova SECRET_KEY segura
            local new_secret_key
            new_secret_key=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
            
            # Substituir SECRET_KEY no .env
            sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=$new_secret_key/" .env
            rm -f .env.bak
            
            log_success "SECRET_KEY corrigida para versão segura"
        else
            log_success "SECRET_KEY já está segura"
        fi
        
        # Verificar se ENVIRONMENT existe
        if ! grep -q "^ENVIRONMENT=" .env; then
            log_info "Adicionando variável ENVIRONMENT..."
            sed -i '1i ENVIRONMENT=production' .env
            log_success "Variável ENVIRONMENT adicionada"
        else
            log_success "Variável ENVIRONMENT já existe"
        fi
        
        # Atualizar ALLOWED_HOSTS se necessário
        if ! grep -q "$server_ip" .env || ! grep -q "$server_hostname" .env; then
            log_info "Atualizando ALLOWED_HOSTS com IP e hostname do servidor..."
            
            # Fazer backup
            cp .env ".env.backup.allowed_hosts.$(date +%Y%m%d_%H%M%S)"
            
            # Atualizar ALLOWED_HOSTS
            local current_allowed_hosts
            current_allowed_hosts=$(grep "^ALLOWED_HOSTS=" .env | cut -d'=' -f2)
            local new_allowed_hosts="localhost,127.0.0.1,0.0.0.0,$server_ip,$server_hostname"
            
            sed -i.bak "s/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$new_allowed_hosts/" .env
            rm -f .env.bak
            
            log_success "ALLOWED_HOSTS atualizado: $new_allowed_hosts"
        else
            log_success "ALLOWED_HOSTS já está configurado corretamente"
        fi
        
        # Atualizar CSRF_TRUSTED_ORIGINS se necessário
        if ! grep -q "$server_ip:8000" .env || ! grep -q "$server_hostname:8000" .env; then
            log_info "Atualizando CSRF_TRUSTED_ORIGINS com IP e hostname do servidor..."
            
            # Fazer backup
            cp .env ".env.backup.csrf.$(date +%Y%m%d_%H%M%S)"
            
            # Atualizar CSRF_TRUSTED_ORIGINS
            local new_csrf_origins="http://localhost:8000,http://127.0.0.1:8000,http://0.0.0.0:8000,http://$server_ip:8000,http://$server_hostname:8000"
            
            if grep -q "^CSRF_TRUSTED_ORIGINS=" .env; then
                sed -i.bak "s/^CSRF_TRUSTED_ORIGINS=.*/CSRF_TRUSTED_ORIGINS=$new_csrf_origins/" .env
            else
                echo "CSRF_TRUSTED_ORIGINS=$new_csrf_origins" >> .env
            fi
            rm -f .env.bak
            
            log_success "CSRF_TRUSTED_ORIGINS atualizado: $new_csrf_origins"
        else
            log_success "CSRF_TRUSTED_ORIGINS já está configurado corretamente"
        fi
        
        return 0
    fi
}

# Função principal de deploy
main() {
    local start_time
    start_time=$(date +%s)
    
    # Inicializar logging
    init_logging
    
    log_section "FireFlies Deploy System"
    log_info "Iniciando deploy automatizado..."
    
    # Garantir que .env existe e SECRET_KEY é segura
    if ! ensure_env_and_secret_key; then
        log_error "Falha ao configurar .env e SECRET_KEY"
        exit 1
    fi
    
    # Parse de argumentos
    parse_arguments "$@"
    
    # Detectar ambiente se não especificado
    if [[ -z "$ENVIRONMENT" ]]; then
        ENVIRONMENT=$(detect_environment)
    fi
    
    log_environment "$ENVIRONMENT"
    log_system_info
    log_network_info
    
    # Validar pré-requisitos
    if [[ "$SKIP_VALIDATION" == "false" ]]; then
        log_section "Validação de Pré-requisitos"
        if ! validate_all "$ENVIRONMENT"; then
            log_error "Validação falhou. Abortando deploy."
            exit 1
        fi
    else
        log_warning "Validação de pré-requisitos pulada"
    fi
    
    # Backup antes do deploy
    if [[ "$BACKUP_BEFORE_DEPLOY" == "true" ]]; then
        log_section "Backup Pré-Deploy"
        backup_docker_volumes "$ENVIRONMENT"
    fi
    
    # Deploy principal
    log_section "Deploy Principal"
    if ! perform_deploy "$ENVIRONMENT"; then
        log_error "Deploy falhou"
        log_conclusion "false" "Deploy falhou" "$(calculate_duration "$start_time")"
        exit 1
    fi
    
    # Health check pós-deploy
    if [[ "$SKIP_HEALTH_CHECK" == "false" ]]; then
        log_section "Health Check Pós-Deploy"
        if ! health_check "$ENVIRONMENT"; then
            log_error "Health check falhou após deploy"
            log_conclusion "false" "Deploy concluído mas health check falhou" "$(calculate_duration "$start_time")"
            exit 1
        fi
    else
        log_warning "Health check pós-deploy pulado"
    fi
    
    # Limpeza pós-deploy
    if [[ "$CLEANUP_AFTER_DEPLOY" == "true" ]]; then
        log_section "Limpeza Pós-Deploy"
        cleanup_docker
    fi
    
    # Monitoramento contínuo
    if [[ "$MONITOR_MODE" == "true" ]]; then
        log_section "Monitoramento Contínuo"
        monitor_health "$ENVIRONMENT" 30
    fi
    
    # Conclusão
    local end_time
    end_time=$(date +%s)
    local duration
    duration=$(calculate_duration "$start_time" "$end_time")
    
    log_conclusion "true" "Deploy concluído com sucesso!" "$duration"
    
    # Exibir informações finais
    show_final_info "$ENVIRONMENT"
}

# Parse de argumentos
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --skip-validation)
                SKIP_VALIDATION=true
                shift
                ;;
            --skip-health-check)
                SKIP_HEALTH_CHECK=true
                shift
                ;;
            --force)
                FORCE_DEPLOY=true
                shift
                ;;
            --no-backup)
                BACKUP_BEFORE_DEPLOY=false
                shift
                ;;
            --cleanup)
                CLEANUP_AFTER_DEPLOY=true
                shift
                ;;
            --monitor)
                MONITOR_MODE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Argumento desconhecido: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Mostrar ajuda
show_help() {
    cat << EOF
FireFlies Deploy System - Sistema de Deploy Automatizado

Uso: $0 [OPÇÕES]

OPÇÕES:
    -e, --environment ENV    Especificar ambiente (development, staging, production)
    --skip-validation        Pular validação de pré-requisitos
    --skip-health-check      Pular health check pós-deploy
    --force                  Forçar deploy mesmo com avisos
    --no-backup             Não fazer backup antes do deploy
    --cleanup               Limpar recursos Docker após deploy
    --monitor               Iniciar monitoramento contínuo
    -h, --help              Mostrar esta ajuda

EXEMPLOS:
    $0                                    # Deploy automático
    $0 -e production                      # Deploy em produção
    $0 -e development --skip-validation   # Deploy dev sem validação
    $0 --monitor                          # Deploy + monitoramento

AMBIENTES SUPORTADOS:
    development    - Ambiente de desenvolvimento
    staging        - Ambiente de homologação
    production     - Ambiente de produção

EOF
}

# Realizar deploy
perform_deploy() {
    local env="$1"
    
    log_step "1" "Preparando ambiente"
    
    # Gerenciar portas automaticamente
    if ! manage_ports "$env"; then
        log_error "Falha ao gerenciar portas"
        return 1
    fi
    
    log_step "2" "Construindo imagem Docker"
    
    # Build da imagem Docker
    if ! build_docker "$env"; then
        log_error "Falha no build Docker"
        return 1
    fi
    
    log_step "3" "Deploy com Docker Compose"
    
    # Deploy com Docker Compose
    if ! deploy_docker "$env"; then
        log_error "Falha no deploy Docker"
        return 1
    fi
    
    log_step "4" "Executando comandos Django"
    
    # Executar comandos Django
    if ! run_django_commands "$env"; then
        log_error "Falha nos comandos Django"
        return 1
    fi
    
    log_step "5" "Verificando saúde dos containers"
    
    # Verificar saúde dos containers
    if ! check_container_health "$env"; then
        log_error "Containers não estão saudáveis"
        return 1
    fi
    
    log_success "Deploy concluído com sucesso!"
    return 0
}

# Calcular duração
calculate_duration() {
    local start_time="$1"
    local end_time="${2:-$(date +%s)}"
    
    local duration
    duration=$((end_time - start_time))
    
    if [[ $duration -lt 60 ]]; then
        echo "${duration}s"
    elif [[ $duration -lt 3600 ]]; then
        local minutes
        minutes=$((duration / 60))
        local seconds
        seconds=$((duration % 60))
        echo "${minutes}m ${seconds}s"
    else
        local hours
        hours=$((duration / 3600))
        local minutes
        minutes=$(( (duration % 3600) / 60 ))
        echo "${hours}h ${minutes}m"
    fi
}

# Mostrar informações finais
show_final_info() {
    local env="$1"
    
    log_section "Informações de Acesso"
    
    # Obter IP da máquina
    local machine_ip
    machine_ip=$(detect_machine_ip)
    
    # Determinar porta da aplicação
    local app_port="8000"
    if [[ -f .env ]]; then
        local env_port
        env_port=$(grep "^DJANGO_PORT=" .env | cut -d'=' -f2)
        if [[ -n "$env_port" ]]; then
            app_port="$env_port"
        fi
    fi
    
    # URLs de acesso
    local urls=(
        "http://localhost:$app_port"
        "http://127.0.0.1:$app_port"
        "http://$machine_ip:$app_port"
    )
    
    log_info "🌐 URLs de acesso:"
    for url in "${urls[@]}"; do
        log_info "  • $url"
    done
    
    # Verificar se é primeira instalação
    if [[ -f .first_install ]]; then
        log_info ""
        log_info "🎯 PRIMEIRA INSTALAÇÃO DETECTADA"
        log_info "Acesse o wizard de configuração para finalizar a instalação:"
        for url in "${urls[@]}"; do
            log_info "  • $url/config/setup/"
        done
    else
        log_info ""
        log_info "🎯 INSTALAÇÃO NORMAL"
        log_info "Sistema pronto para uso!"
    fi
    
    # Informações de administração
    log_info ""
    log_info "🔧 Comandos úteis:"
    log_info "  • Ver logs: docker-compose logs -f"
    log_info "  • Parar sistema: docker-compose down"
    log_info "  • Reiniciar: docker-compose restart"
    log_info "  • Health check: $0 --health-check"
    
    # Informações de backup
    if [[ "$BACKUP_BEFORE_DEPLOY" == "true" ]]; then
        log_info ""
        log_info "💾 Backup criado em: backups/docker/"
    fi
}

# Funções auxiliares para comandos específicos

# Comando de health check
health_check_command() {
    local env="$1"
    
    log_section "Health Check"
    
    if health_check "$env"; then
        log_success "Health check: TODOS OS SISTEMAS SAUDÁVEIS"
        exit 0
    else
        log_error "Health check: PROBLEMAS DETECTADOS"
        exit 1
    fi
}

# Comando de backup
backup_command() {
    local env="$1"
    
    log_section "Backup"
    
    if backup_docker_volumes "$env"; then
        log_success "Backup concluído com sucesso"
        exit 0
    else
        log_error "Falha no backup"
        exit 1
    fi
}

# Comando de restore
restore_command() {
    local env="$1"
    local backup_file="$2"
    
    log_section "Restore"
    
    if restore_docker_volumes "$env" "$backup_file"; then
        log_success "Restore concluído com sucesso"
        exit 0
    else
        log_error "Falha no restore"
        exit 1
    fi
}

# Comando de monitoramento
monitor_command() {
    local env="$1"
    local interval="${2:-30}"
    
    log_section "Monitoramento Contínuo"
    log_info "Iniciando monitoramento (intervalo: ${interval}s)"
    log_info "Pressione Ctrl+C para parar"
    
    monitor_health "$env" "$interval"
}

# Comando de limpeza
cleanup_command() {
    log_section "Limpeza"
    
    cleanup_docker
    cleanup_logs "logs" 7
    
    log_success "Limpeza concluída"
}

# Comando de logs
logs_command() {
    local env="$1"
    local service="$2"
    local lines="${3:-100}"
    
    log_section "Logs"
    
    get_docker_logs "$env" "$service" "$lines"
}

# Comando de status
status_command() {
    local env="$1"
    
    log_section "Status do Sistema"
    
    # Status dos containers
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    log_info "Status dos containers:"
    docker-compose -f "$compose_file" ps
    
    # Recursos do sistema
    log_info ""
    log_info "Recursos do sistema:"
    monitor_docker_resources
    
    # Health check rápido
    log_info ""
    log_info "Health check rápido:"
    if quick_health_check "$env"; then
        log_success "Sistema saudável"
    else
        log_error "Problemas detectados"
    fi
}

# Handler de sinais
cleanup_on_exit() {
    log_warning "Interrupção detectada. Limpando..."
    
    # Parar containers se necessário
    if [[ -n "${ENVIRONMENT:-}" ]]; then
        local compose_file="docker-compose.yml"
        if [[ "$ENVIRONMENT" == "development" ]]; then
            compose_file="docker-compose.dev.yml"
        fi
        
        if [[ -f "$compose_file" ]]; then
            log_info "Parando containers..."
            docker-compose -f "$compose_file" down --remove-orphans || true
        fi
    fi
    
    log_info "Limpeza concluída"
    exit 1
}

# Configurar handlers de sinal
trap cleanup_on_exit INT TERM

# Verificar se é um comando específico
case "${1:-}" in
    health-check|health)
        health_check_command "${2:-$(detect_environment)}"
        ;;
    backup)
        backup_command "${2:-$(detect_environment)}"
        ;;
    restore)
        restore_command "${2:-$(detect_environment)}" "${3:-}"
        ;;
    monitor)
        monitor_command "${2:-$(detect_environment)}" "${3:-30}"
        ;;
    cleanup)
        cleanup_command
        ;;
    logs)
        logs_command "${2:-$(detect_environment)}" "${3:-}" "${4:-100}"
        ;;
    status)
        status_command "${2:-$(detect_environment)}"
        ;;
    *)
        # Comando padrão: deploy
        main "$@"
        ;;
esac 