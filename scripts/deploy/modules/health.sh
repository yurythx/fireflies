#!/bin/bash

# Módulo Health Check - FireFlies Deploy
# Verificações de saúde da aplicação e sistema

# Health check principal
health_check() {
    local env="$1"
    log_info "Iniciando health check completo..."
    
    local all_healthy=true
    
    # Verificar saúde dos containers
    if ! check_container_health "$env"; then
        all_healthy=false
    fi
    
    # Verificar conectividade da aplicação
    if ! check_application_health "$env"; then
        all_healthy=false
    fi
    
    # Verificar banco de dados
    if ! check_database_health "$env"; then
        all_healthy=false
    fi
    
    # Verificar cache Redis
    if ! check_redis_health "$env"; then
        all_healthy=false
    fi
    
    # Verificar recursos do sistema
    if ! check_system_health; then
        all_healthy=false
    fi
    
    if [[ "$all_healthy" == "true" ]]; then
        log_success "Health check completo: TODOS OS SISTEMAS SAUDÁVEIS"
        return 0
    else
        log_error "Health check completo: PROBLEMAS DETECTADOS"
        return 1
    fi
}

# Verificar saúde dos containers
check_container_health() {
    local env="$1"
    log_info "Verificando saúde dos containers..."
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Verificar se containers estão rodando
    local running_containers
    running_containers=$(docker-compose -f "$compose_file" ps -q | wc -l)
    local total_containers
    total_containers=$(docker-compose -f "$compose_file" config --services | wc -l)
    
    if [[ $running_containers -eq $total_containers ]]; then
        log_success "Todos os containers estão rodando ($running_containers/$total_containers)"
        
        # Verificar health checks individuais dos containers
        local services
        services=$(docker-compose -f "$compose_file" config --services)
        
        for service in $services; do
            if ! check_service_health "$compose_file" "$service"; then
                log_error "Container $service não está saudável"
                return 1
            fi
        done
        
        return 0
    else
        log_error "Containers não estão rodando ($running_containers/$total_containers)"
        return 1
    fi
}

# Verificar saúde de um serviço específico
check_service_health() {
    local compose_file="$1"
    local service="$2"
    
    # Verificar se o container tem health check configurado
    local health_status
    health_status=$(docker-compose -f "$compose_file" ps -q "$service" | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null)
    
    if [[ -n "$health_status" ]]; then
        if [[ "$health_status" == "healthy" ]]; then
            log_success "Serviço $service: saudável"
            return 0
        elif [[ "$health_status" == "unhealthy" ]]; then
            log_error "Serviço $service: não saudável"
            return 1
        else
            log_warning "Serviço $service: status desconhecido ($health_status)"
            return 0  # Não falhar para status desconhecido
        fi
    else
        # Se não tem health check, verificar se está rodando
        local container_status
        container_status=$(docker-compose -f "$compose_file" ps -q "$service" | xargs docker inspect --format='{{.State.Status}}' 2>/dev/null)
        
        if [[ "$container_status" == "running" ]]; then
            log_success "Serviço $service: rodando"
            return 0
        else
            log_error "Serviço $service: não está rodando ($container_status)"
            return 1
        fi
    fi
}

# Verificar conectividade da aplicação
check_application_health() {
    local env="$1"
    log_info "Verificando conectividade da aplicação..."
    
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
    
    # Endpoints para testar
    local endpoints=(
        "http://localhost:$app_port/health/"
        "http://127.0.0.1:$app_port/health/"
        "http://$machine_ip:$app_port/health/"
    )
    
    local endpoint_accessible=false
    
    for endpoint in "${endpoints[@]}"; do
        if check_endpoint "$endpoint"; then
            log_success "Aplicação acessível em: $endpoint"
            endpoint_accessible=true
            break
        fi
    done
    
    if [[ "$endpoint_accessible" == "false" ]]; then
        log_error "Aplicação não está acessível"
        return 1
    fi
    
    # Verificar se é primeira instalação
    if [[ -f .first_install ]]; then
        log_info "Primeira instalação detectada - verificando wizard..."
        
        local wizard_endpoints=(
            "http://localhost:$app_port/config/setup/"
            "http://127.0.0.1:$app_port/config/setup/"
            "http://$machine_ip:$app_port/config/setup/"
        )
        
        for endpoint in "${wizard_endpoints[@]}"; do
            if check_endpoint "$endpoint"; then
                log_success "Wizard de configuração acessível em: $endpoint"
                return 0
            fi
        done
        
        log_error "Wizard de configuração não está acessível"
        return 1
    fi
    
    return 0
}

# Verificar endpoint HTTP
check_endpoint() {
    local endpoint="$1"
    
    # Tentar com curl
    if command -v curl &> /dev/null; then
        if curl -f -s --max-time 10 "$endpoint" &> /dev/null; then
            return 0
        fi
    fi
    
    # Tentar com wget
    if command -v wget &> /dev/null; then
        if wget -q --timeout=10 --tries=1 "$endpoint" -O /dev/null &> /dev/null; then
            return 0
        fi
    fi
    
    return 1
}

# Verificar saúde do banco de dados
check_database_health() {
    local env="$1"
    log_info "Verificando saúde do banco de dados..."
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Verificar se o container do banco está rodando
    if ! docker-compose -f "$compose_file" ps -q db &> /dev/null; then
        log_error "Container do banco de dados não encontrado"
        return 1
    fi
    
    # Testar conexão com o banco
    if ! docker-compose -f "$compose_file" exec -T db pg_isready -U postgres &> /dev/null; then
        log_error "Banco de dados não está respondendo"
        return 1
    fi
    
    # Verificar se as tabelas Django existem
    if ! docker-compose -f "$compose_file" exec -T web python manage.py check --database default &> /dev/null; then
        log_error "Problemas com a conexão Django-Database"
        return 1
    fi
    
    log_success "Banco de dados saudável"
    return 0
}

# Verificar saúde do Redis
check_redis_health() {
    local env="$1"
    log_info "Verificando saúde do Redis..."
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Verificar se o container do Redis está rodando
    if ! docker-compose -f "$compose_file" ps -q redis &> /dev/null; then
        log_warning "Container do Redis não encontrado (opcional)"
        return 0
    fi
    
    # Testar conexão com o Redis
    if ! docker-compose -f "$compose_file" exec -T redis redis-cli ping &> /dev/null; then
        log_error "Redis não está respondendo"
        return 1
    fi
    
    log_success "Redis saudável"
    return 0
}

# Verificar saúde do sistema
check_system_health() {
    log_info "Verificando saúde do sistema..."
    
    local system_healthy=true
    
    # Verificar uso de CPU
    if command -v top &> /dev/null; then
        local cpu_usage
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
        
        if [[ $(echo "$cpu_usage > 90" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
            log_warning "Uso de CPU alto: ${cpu_usage}%"
        else
            log_success "Uso de CPU: ${cpu_usage}%"
        fi
    fi
    
    # Verificar uso de memória
    if command -v free &> /dev/null; then
        local mem_usage
        mem_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
        
        if [[ $(echo "$mem_usage > 90" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
            log_warning "Uso de memória alto: ${mem_usage}%"
            system_healthy=false
        else
            log_success "Uso de memória: ${mem_usage}%"
        fi
    fi
    
    # Verificar espaço em disco
    if command -v df &> /dev/null; then
        local disk_usage
        disk_usage=$(df . | awk 'NR==2{printf "%.1f", $5}' | sed 's/%//')
        
        if [[ $(echo "$disk_usage > 90" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
            log_warning "Uso de disco alto: ${disk_usage}%"
            system_healthy=false
        else
            log_success "Uso de disco: ${disk_usage}%"
        fi
    fi
    
    # Verificar conectividade de rede
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        log_warning "Problemas de conectividade de rede"
    else
        log_success "Conectividade de rede OK"
    fi
    
    if [[ "$system_healthy" == "true" ]]; then
        return 0
    else
        return 1
    fi
}

# Health check rápido (para uso em CI/CD)
quick_health_check() {
    local env="$1"
    log_info "Executando health check rápido..."
    
    # Verificar apenas se a aplicação está respondendo
    local machine_ip
    machine_ip=$(detect_machine_ip)
    
    local app_port="8000"
    if [[ -f .env ]]; then
        local env_port
        env_port=$(grep "^DJANGO_PORT=" .env | cut -d'=' -f2)
        if [[ -n "$env_port" ]]; then
            app_port="$env_port"
        fi
    fi
    
    local endpoint="http://localhost:$app_port/health/"
    
    if check_endpoint "$endpoint"; then
        log_success "Health check rápido: OK"
        return 0
    else
        log_error "Health check rápido: FALHOU"
        return 1
    fi
}

# Health check detalhado com métricas
detailed_health_check() {
    local env="$1"
    log_info "Executando health check detalhado..."
    
    # Coletar métricas
    local metrics=()
    
    # Métricas de containers
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    local running_containers
    running_containers=$(docker-compose -f "$compose_file" ps -q | wc -l)
    local total_containers
    total_containers=$(docker-compose -f "$compose_file" config --services | wc -l)
    
    metrics+=("containers_running=$running_containers")
    metrics+=("containers_total=$total_containers")
    
    # Métricas de recursos
    if command -v free &> /dev/null; then
        local mem_usage
        mem_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
        metrics+=("memory_usage=$mem_usage")
    fi
    
    if command -v df &> /dev/null; then
        local disk_usage
        disk_usage=$(df . | awk 'NR==2{printf "%.1f", $5}' | sed 's/%//')
        metrics+=("disk_usage=$disk_usage")
    fi
    
    # Métricas de conectividade
    local machine_ip
    machine_ip=$(detect_machine_ip)
    local app_port="8000"
    
    if [[ -f .env ]]; then
        local env_port
        env_port=$(grep "^DJANGO_PORT=" .env | cut -d'=' -f2)
        if [[ -n "$env_port" ]]; then
            app_port="$env_port"
        fi
    fi
    
    local endpoint="http://localhost:$app_port/health/"
    if check_endpoint "$endpoint"; then
        metrics+=("app_accessible=true")
    else
        metrics+=("app_accessible=false")
    fi
    
    # Exibir métricas
    log_info "Métricas de saúde:"
    for metric in "${metrics[@]}"; do
        log_info "  $metric"
    done
    
    # Salvar métricas em arquivo
    local metrics_file="logs/health_metrics_$(date +%Y%m%d_%H%M%S).txt"
    mkdir -p logs
    printf "%s\n" "${metrics[@]}" > "$metrics_file"
    
    log_success "Métricas salvas em: $metrics_file"
}

# Monitoramento contínuo
monitor_health() {
    local env="$1"
    local interval="${2:-30}"  # Intervalo em segundos
    
    log_info "Iniciando monitoramento contínuo (intervalo: ${interval}s)..."
    
    while true; do
        log_info "=== Health Check $(date) ==="
        
        if ! quick_health_check "$env"; then
            log_error "Problema detectado no health check!"
            # Aqui você pode adicionar notificações (email, Slack, etc.)
        fi
        
        sleep "$interval"
    done
}

# Verificar logs de erro
check_error_logs() {
    local env="$1"
    log_info "Verificando logs de erro..."
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Verificar logs dos últimos 10 minutos
    local error_count
    error_count=$(docker-compose -f "$compose_file" logs --since="10m" | grep -i "error\|exception\|traceback" | wc -l)
    
    if [[ $error_count -gt 0 ]]; then
        log_warning "Encontrados $error_count erros nos últimos 10 minutos"
        
        # Mostrar últimos erros
        log_info "Últimos erros:"
        docker-compose -f "$compose_file" logs --since="10m" | grep -i "error\|exception\|traceback" | tail -5
    else
        log_success "Nenhum erro encontrado nos últimos 10 minutos"
    fi
} 