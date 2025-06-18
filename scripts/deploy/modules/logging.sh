#!/bin/bash

# Módulo de Logging - FireFlies Deploy
# Sistema de logging estruturado e colorido

# Configurações de logging
readonly LOG_LEVEL_DEBUG=0
readonly LOG_LEVEL_INFO=1
readonly LOG_LEVEL_WARNING=2
readonly LOG_LEVEL_ERROR=3

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Variáveis globais de logging
LOG_LEVEL=${LOG_LEVEL:-$LOG_LEVEL_INFO}
LOG_FILE=${LOG_FILE:-""}
LOG_TO_FILE=false

# Inicializar sistema de logging
init_logging() {
    # Verificar se deve logar para arquivo
    if [[ -n "$LOG_FILE" ]]; then
        LOG_TO_FILE=true
        # Criar diretório de logs se não existir
        local log_dir
        log_dir=$(dirname "$LOG_FILE")
        if [[ ! -d "$log_dir" ]]; then
            mkdir -p "$log_dir"
        fi
    fi
    
    log_info "Sistema de logging inicializado"
    log_debug "Nível de log: $LOG_LEVEL"
    if [[ "$LOG_TO_FILE" == "true" ]]; then
        log_debug "Logging para arquivo: $LOG_FILE"
    fi
}

# Função base de logging
_log() {
    local level="$1"
    local color="$2"
    local level_name="$3"
    local message="$4"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Verificar nível de log
    if [[ $level -lt $LOG_LEVEL ]]; then
        return
    fi
    
    # Formatar mensagem
    local formatted_message="[${timestamp}] [${level_name}] ${message}"
    
    # Output para console com cor
    echo -e "${color}${formatted_message}${NC}"
    
    # Output para arquivo (sem cor)
    if [[ "$LOG_TO_FILE" == "true" ]]; then
        echo "${formatted_message}" >> "$LOG_FILE"
    fi
}

# Funções de logging por nível
log_debug() {
    _log $LOG_LEVEL_DEBUG "$CYAN" "DEBUG" "$1"
}

log_info() {
    _log $LOG_LEVEL_INFO "$BLUE" "INFO" "$1"
}

log_warning() {
    _log $LOG_LEVEL_WARNING "$YELLOW" "WARNING" "$1"
}

log_error() {
    _log $LOG_LEVEL_ERROR "$RED" "ERROR" "$1"
}

log_success() {
    _log $LOG_LEVEL_INFO "$GREEN" "SUCCESS" "$1"
}

# Logging especializado
log_step() {
    local step="$1"
    local message="$2"
    log_info "=== PASSO $step ==="
    log_info "$message"
}

log_section() {
    local section="$1"
    log_info ""
    log_info "🔧 $section"
    log_info "=================================="
}

log_subsection() {
    local subsection="$1"
    log_info ""
    log_info "📋 $subsection"
    log_info "----------------------------------"
}

log_command() {
    local command="$1"
    log_debug "Executando comando: $command"
}

log_result() {
    local success="$1"
    local message="$2"
    
    if [[ "$success" == "true" ]]; then
        log_success "✅ $message"
    else
        log_error "❌ $message"
    fi
}

# Logging de métricas
log_metric() {
    local metric="$1"
    local value="$2"
    local unit="${3:-}"
    
    if [[ -n "$unit" ]]; then
        log_info "📊 $metric: $value $unit"
    else
        log_info "📊 $metric: $value"
    fi
}

# Logging de progresso
log_progress() {
    local current="$1"
    local total="$2"
    local message="$3"
    
    local percentage
    percentage=$((current * 100 / total))
    
    log_info "🔄 Progresso: $current/$total ($percentage%) - $message"
}

# Logging de tempo
log_timing() {
    local operation="$1"
    local start_time="$2"
    local end_time="$3"
    
    local duration
    duration=$((end_time - start_time))
    
    if [[ $duration -lt 60 ]]; then
        log_info "⏱️  $operation concluído em ${duration}s"
    elif [[ $duration -lt 3600 ]]; then
        local minutes
        minutes=$((duration / 60))
        local seconds
        seconds=$((duration % 60))
        log_info "⏱️  $operation concluído em ${minutes}m ${seconds}s"
    else
        local hours
        hours=$((duration / 3600))
        local minutes
        minutes=$(( (duration % 3600) / 60 ))
        log_info "⏱️  $operation concluído em ${hours}h ${minutes}m"
    fi
}

# Logging de erro detalhado
log_error_details() {
    local error_message="$1"
    local error_code="${2:-}"
    local stack_trace="${3:-}"
    
    log_error "$error_message"
    
    if [[ -n "$error_code" ]]; then
        log_error "Código de erro: $error_code"
    fi
    
    if [[ -n "$stack_trace" ]]; then
        log_debug "Stack trace:"
        echo "$stack_trace" | while IFS= read -r line; do
            log_debug "  $line"
        done
    fi
}

# Logging de configuração
log_config() {
    local config_name="$1"
    local config_value="$2"
    
    # Mascarar valores sensíveis
    case "$config_name" in
        *password*|*secret*|*key*|*token*)
            local masked_value
            masked_value=$(echo "$config_value" | sed 's/./*/g')
            log_debug "Config: $config_name = $masked_value"
            ;;
        *)
            log_debug "Config: $config_name = $config_value"
            ;;
    esac
}

# Logging de ambiente
log_environment() {
    local env="$1"
    
    log_info "🌍 Ambiente detectado: $env"
    
    # Log de variáveis de ambiente relevantes
    local relevant_vars=("ENVIRONMENT" "DEBUG" "DJANGO_SETTINGS_MODULE" "DATABASE_URL")
    
    for var in "${relevant_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            log_config "$var" "${!var}"
        fi
    done
}

# Logging de sistema
log_system_info() {
    log_info "💻 Informações do sistema:"
    
    # Sistema operacional
    if command -v uname &> /dev/null; then
        local os_info
        os_info=$(uname -a)
        log_info "  OS: $os_info"
    fi
    
    # Versão do Docker
    if command -v docker &> /dev/null; then
        local docker_version
        docker_version=$(docker --version)
        log_info "  Docker: $docker_version"
    fi
    
    # Versão do Docker Compose
    if command -v docker-compose &> /dev/null; then
        local compose_version
        compose_version=$(docker-compose --version)
        log_info "  Docker Compose: $compose_version"
    fi
    
    # Memória disponível
    if command -v free &> /dev/null; then
        local mem_info
        mem_info=$(free -h | awk 'NR==2{printf "%.1f GB", $2/1024}')
        log_info "  Memória: $mem_info"
    fi
    
    # Espaço em disco
    if command -v df &> /dev/null; then
        local disk_info
        disk_info=$(df -h . | awk 'NR==2{print $4}')
        log_info "  Espaço livre: $disk_info"
    fi
}

# Logging de rede
log_network_info() {
    log_info "🌐 Informações de rede:"
    
    # IP da máquina
    local machine_ip
    machine_ip=$(detect_machine_ip)
    log_info "  IP: $machine_ip"
    
    # Hostname
    if command -v hostname &> /dev/null; then
        local hostname
        hostname=$(hostname)
        log_info "  Hostname: $hostname"
    fi
    
    # Conectividade
    if ping -c 1 8.8.8.8 &> /dev/null; then
        log_success "  Conectividade: OK"
    else
        log_warning "  Conectividade: Problemas detectados"
    fi
}

# Logging de arquivos
log_file_operation() {
    local operation="$1"
    local file_path="$2"
    local success="$3"
    
    case "$operation" in
        "create")
            if [[ "$success" == "true" ]]; then
                log_success "📄 Arquivo criado: $file_path"
            else
                log_error "📄 Falha ao criar arquivo: $file_path"
            fi
            ;;
        "update")
            if [[ "$success" == "true" ]]; then
                log_success "📝 Arquivo atualizado: $file_path"
            else
                log_error "📝 Falha ao atualizar arquivo: $file_path"
            fi
            ;;
        "delete")
            if [[ "$success" == "true" ]]; then
                log_success "🗑️  Arquivo removido: $file_path"
            else
                log_error "🗑️  Falha ao remover arquivo: $file_path"
            fi
            ;;
        "backup")
            if [[ "$success" == "true" ]]; then
                log_success "💾 Backup criado: $file_path"
            else
                log_error "💾 Falha ao criar backup: $file_path"
            fi
            ;;
    esac
}

# Logging de Docker
log_docker_operation() {
    local operation="$1"
    local target="$2"
    local success="$3"
    
    case "$operation" in
        "build")
            if [[ "$success" == "true" ]]; then
                log_success "🐳 Imagem construída: $target"
            else
                log_error "🐳 Falha ao construir imagem: $target"
            fi
            ;;
        "start")
            if [[ "$success" == "true" ]]; then
                log_success "🚀 Container iniciado: $target"
            else
                log_error "🚀 Falha ao iniciar container: $target"
            fi
            ;;
        "stop")
            if [[ "$success" == "true" ]]; then
                log_success "🛑 Container parado: $target"
            else
                log_error "🛑 Falha ao parar container: $target"
            fi
            ;;
        "restart")
            if [[ "$success" == "true" ]]; then
                log_success "🔄 Container reiniciado: $target"
            else
                log_error "🔄 Falha ao reiniciar container: $target"
            fi
            ;;
    esac
}

# Logging de validação
log_validation() {
    local component="$1"
    local success="$2"
    local details="${3:-}"
    
    if [[ "$success" == "true" ]]; then
        log_success "✅ Validação $component: OK"
    else
        log_error "❌ Validação $component: FALHOU"
        if [[ -n "$details" ]]; then
            log_error "  Detalhes: $details"
        fi
    fi
}

# Logging de resumo
log_summary() {
    local title="$1"
    local items=("${@:2}")
    
    log_info ""
    log_info "📋 $title"
    log_info "=================================="
    
    for item in "${items[@]}"; do
        log_info "  • $item"
    done
    
    log_info "=================================="
}

# Logging de conclusão
log_conclusion() {
    local success="$1"
    local message="$2"
    local duration="${3:-}"
    
    log_info ""
    log_info "🎯 CONCLUSÃO"
    log_info "=================================="
    
    if [[ "$success" == "true" ]]; then
        log_success "✅ $message"
    else
        log_error "❌ $message"
    fi
    
    if [[ -n "$duration" ]]; then
        log_info "⏱️  Tempo total: $duration"
    fi
    
    log_info "=================================="
}

# Função para limpar logs antigos
cleanup_logs() {
    local log_dir="$1"
    local days_to_keep="${2:-7}"
    
    if [[ -d "$log_dir" ]]; then
        log_info "🧹 Limpando logs antigos (mais de $days_to_keep dias)..."
        
        local deleted_count
        deleted_count=$(find "$log_dir" -name "*.log" -mtime +$days_to_keep -delete -print | wc -l)
        
        if [[ $deleted_count -gt 0 ]]; then
            log_success "Removidos $deleted_count arquivos de log antigos"
        else
            log_info "Nenhum arquivo de log antigo encontrado"
        fi
    fi
}

# Função para rotacionar logs
rotate_logs() {
    local log_file="$1"
    local max_size_mb="${2:-10}"
    
    if [[ -f "$log_file" ]]; then
        local file_size_mb
        file_size_mb=$(du -m "$log_file" | cut -f1)
        
        if [[ $file_size_mb -gt $max_size_mb ]]; then
            local timestamp
            timestamp=$(date +%Y%m%d_%H%M%S)
            local backup_file="${log_file}.${timestamp}"
            
            log_info "📦 Rotacionando log: $log_file -> $backup_file"
            mv "$log_file" "$backup_file"
            
            # Comprimir backup
            if command -v gzip &> /dev/null; then
                gzip "$backup_file"
                log_success "Log comprimido: ${backup_file}.gz"
            fi
        fi
    fi
} 