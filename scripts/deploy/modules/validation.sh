#!/bin/bash

# Módulo de Validação - FireFlies Deploy
# Validações robustas e verificações de pré-requisitos

# Verificar pré-requisitos do sistema
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
    local all_good=true
    
    # Verificar Docker
    if ! check_docker; then
        all_good=false
    fi
    
    # Verificar Docker Compose
    if ! check_docker_compose; then
        all_good=false
    fi
    
    # Verificar Python (opcional para Docker)
    if ! check_python; then
        log_warning "Python não encontrado (opcional para Docker)"
    fi
    
    # Verificar ferramentas do sistema
    if ! check_system_tools; then
        all_good=false
    fi
    
    # Verificar permissões
    if ! check_permissions; then
        all_good=false
    fi
    
    if [[ "$all_good" == "true" ]]; then
        log_success "Todos os pré-requisitos atendidos"
        return 0
    else
        log_error "Pré-requisitos não atendidos"
        return 1
    fi
}

# Verificar Docker
check_docker() {
    if command -v docker &> /dev/null; then
        local docker_version
        docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker $docker_version encontrado"
        
        # Verificar se Docker está rodando
        if ! docker info &> /dev/null; then
            log_error "Docker não está rodando"
            log_info "Para iniciar o Docker:"
            log_info "  Linux: sudo systemctl start docker"
            log_info "  macOS: open -a Docker"
            log_info "  Windows: Inicie o Docker Desktop"
            return 1
        fi
        
        return 0
    else
        log_error "Docker não encontrado"
        log_info "Instale Docker:"
        log_info "  Ubuntu/Debian: sudo apt install docker.io docker-compose"
        log_info "  macOS: brew install docker docker-compose"
        log_info "  Ou siga: https://docs.docker.com/engine/install/"
        return 1
    fi
}

# Verificar Docker Compose
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        local compose_version
        compose_version=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker Compose $compose_version encontrado"
        return 0
    else
        log_error "Docker Compose não encontrado"
        log_info "Instale Docker Compose:"
        log_info "  Ubuntu/Debian: sudo apt install docker-compose"
        log_info "  Ou: sudo curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose"
        return 1
    fi
}

# Verificar Python
check_python() {
    if command -v python3 &> /dev/null; then
        local python_version
        python_version=$(python3 --version | cut -d' ' -f2)
        log_success "Python $python_version encontrado"
        return 0
    elif command -v python &> /dev/null; then
        local python_version
        python_version=$(python --version | cut -d' ' -f2)
        log_success "Python $python_version encontrado"
        return 0
    else
        return 1
    fi
}

# Verificar ferramentas do sistema
check_system_tools() {
    local tools=("curl" "wget" "git")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_warning "Ferramentas ausentes: ${missing_tools[*]}"
        log_info "Instalando ferramentas..."
        
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y "${missing_tools[@]}"
        elif command -v yum &> /dev/null; then
            sudo yum install -y "${missing_tools[@]}"
        elif command -v brew &> /dev/null; then
            brew install "${missing_tools[@]}"
        else
            log_warning "Não foi possível instalar ferramentas automaticamente"
            return 1
        fi
    fi
    
    return 0
}

# Verificar permissões
check_permissions() {
    # Verificar se usuário está no grupo docker
    if command -v groups &> /dev/null; then
        if ! groups | grep -q docker; then
            log_warning "Usuário não está no grupo docker"
            log_info "Para adicionar: sudo usermod -aG docker $USER"
            log_info "Reinicie a sessão após adicionar ao grupo"
        fi
    fi
    
    # Verificar permissões de escrita no diretório atual
    if [[ ! -w . ]]; then
        log_error "Sem permissão de escrita no diretório atual"
        return 1
    fi
    
    return 0
}

# Validar configuração do ambiente
validate_environment_config() {
    local env="$1"
    
    log_info "Validando configuração do ambiente: $env"
    
    # Verificar arquivo .env
    if [[ ! -f .env ]]; then
        log_error "Arquivo .env não encontrado"
        return 1
    fi
    
    # Verificar variáveis obrigatórias
    local required_vars=("ENVIRONMENT" "SECRET_KEY" "DEBUG")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Variáveis obrigatórias ausentes: ${missing_vars[*]}"
        return 1
    fi
    
    # Verificar configurações específicas do ambiente
    if [[ "$env" == "production" ]]; then
        if ! validate_production_config; then
            return 1
        fi
    fi
    
    log_success "Configuração do ambiente validada"
    return 0
}

# Validar configuração de produção
validate_production_config() {
    log_info "Validando configurações de produção..."
    
    # Verificar se DEBUG está desabilitado
    if grep -q "^DEBUG=True" .env; then
        log_error "DEBUG deve ser False em produção"
        return 1
    fi
    
    # Verificar ALLOWED_HOSTS
    if grep -q "^ALLOWED_HOSTS=\*" .env; then
        log_error "ALLOWED_HOSTS não deve ser '*' em produção"
        return 1
    fi
    
    # Verificar SECRET_KEY
    if grep -q "^SECRET_KEY=django-insecure" .env; then
        log_error "SECRET_KEY deve ser alterada em produção"
        return 1
    fi
    
    return 0
}

# Validar portas disponíveis
validate_ports() {
    local env="$1"
    
    log_info "Validando portas disponíveis..."
    
    local required_ports=()
    
    if [[ "$env" == "development" ]]; then
        required_ports=(8000 5432 6379)
    else
        required_ports=(8000 5432 6379 80 443)
    fi
    
    local occupied_ports=()
    
    for port in "${required_ports[@]}"; do
        if lsof -i ":$port" &> /dev/null; then
            occupied_ports+=("$port")
        fi
    done
    
    if [[ ${#occupied_ports[@]} -gt 0 ]]; then
        log_warning "Portas ocupadas: ${occupied_ports[*]}"
        log_info "O sistema tentará usar portas alternativas"
    fi
    
    return 0
}

# Validar conectividade de rede
validate_network() {
    log_info "Validando conectividade de rede..."
    
    # Testar conectividade com internet
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        log_warning "Sem conectividade com internet"
    else
        log_success "Conectividade com internet OK"
    fi
    
    # Testar DNS
    if ! nslookup google.com &> /dev/null; then
        log_warning "Problemas com DNS"
    else
        log_success "DNS funcionando"
    fi
    
    return 0
}

# Validar recursos do sistema
validate_system_resources() {
    log_info "Validando recursos do sistema..."
    
    # Verificar memória disponível
    if command -v free &> /dev/null; then
        local mem_available
        mem_available=$(free -m | awk 'NR==2{printf "%.0f", $7}')
        
        if [[ $mem_available -lt 512 ]]; then
            log_warning "Pouca memória disponível: ${mem_available}MB"
            log_info "Recomendado: pelo menos 1GB"
        else
            log_success "Memória disponível: ${mem_available}MB"
        fi
    fi
    
    # Verificar espaço em disco
    if command -v df &> /dev/null; then
        local disk_usage
        disk_usage=$(df . | awk 'NR==2{printf "%.0f", $5}' | sed 's/%//')
        
        if [[ $disk_usage -gt 90 ]]; then
            log_warning "Pouco espaço em disco: ${disk_usage}% usado"
        else
            log_success "Espaço em disco: ${disk_usage}% usado"
        fi
    fi
    
    return 0
}

# Validar arquivos de configuração Docker
validate_docker_files() {
    local env="$1"
    
    log_info "Validando arquivos Docker..."
    
    # Verificar Dockerfile
    local dockerfile="Dockerfile"
    if [[ "$env" == "development" ]]; then
        dockerfile="Dockerfile.dev"
    fi
    
    if [[ ! -f "$dockerfile" ]]; then
        log_error "Dockerfile $dockerfile não encontrado"
        return 1
    fi
    
    # Verificar docker-compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    if [[ ! -f "$compose_file" ]]; then
        log_error "Arquivo $compose_file não encontrado"
        return 1
    fi
    
    # Validar sintaxe do docker-compose
    if ! docker-compose -f "$compose_file" config &> /dev/null; then
        log_error "Erro de sintaxe no $compose_file"
        return 1
    fi
    
    log_success "Arquivos Docker validados"
    return 0
}

# Função principal de validação
validate_all() {
    local env="$1"
    
    log_info "Iniciando validação completa..."
    
    local all_valid=true
    
    # Validar pré-requisitos
    if ! check_prerequisites; then
        all_valid=false
    fi
    
    # Validar configuração do ambiente
    if ! validate_environment_config "$env"; then
        all_valid=false
    fi
    
    # Validar portas
    if ! validate_ports "$env"; then
        all_valid=false
    fi
    
    # Validar rede
    if ! validate_network; then
        all_valid=false
    fi
    
    # Validar recursos
    if ! validate_system_resources; then
        all_valid=false
    fi
    
    # Validar arquivos Docker
    if ! validate_docker_files "$env"; then
        all_valid=false
    fi
    
    if [[ "$all_valid" == "true" ]]; then
        log_success "Validação completa concluída com sucesso"
        return 0
    else
        log_error "Validação falhou"
        return 1
    fi
} 