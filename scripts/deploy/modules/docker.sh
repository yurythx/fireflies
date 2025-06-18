#!/bin/bash

# Módulo Docker - FireFlies Deploy
# Gerencia operações Docker e Docker Compose

# Build da imagem Docker
build_docker() {
    local env="$1"
    log_info "Construindo imagem Docker para ambiente: $env"
    
    # Determinar Dockerfile
    local dockerfile="Dockerfile"
    if [[ "$env" == "development" ]]; then
        dockerfile="Dockerfile.dev"
    fi
    
    if [[ ! -f "$dockerfile" ]]; then
        log_error "Dockerfile $dockerfile não encontrado"
        return 1
    fi
    
    # Construir imagem com cache otimizado
    local build_args=""
    if [[ "$env" == "production" ]]; then
        build_args="--build-arg ENVIRONMENT=production --build-arg DJANGO_SETTINGS_MODULE=core.settings"
    else
        build_args="--build-arg ENVIRONMENT=development --build-arg DJANGO_SETTINGS_MODULE=core.settings_dev"
    fi
    
    log_info "Executando build com Dockerfile: $dockerfile"
    
    if docker build -f "$dockerfile" $build_args -t "fireflies:$env" .; then
        log_success "Imagem Docker construída com sucesso"
        return 0
    else
        log_error "Falha ao construir imagem Docker"
        return 1
    fi
}

# Deploy com Docker Compose
deploy_docker() {
    local env="$1"
    log_info "Iniciando deploy com Docker Compose..."
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    if [[ ! -f "$compose_file" ]]; then
        log_error "Arquivo $compose_file não encontrado"
        return 1
    fi
    
    # Validar sintaxe do docker-compose
    log_info "Validando sintaxe do docker-compose..."
    if ! docker-compose -f "$compose_file" config &> /dev/null; then
        log_error "Erro de sintaxe no $compose_file"
        return 1
    fi
    
    # Parar containers existentes
    log_info "Parando containers existentes..."
    docker-compose -f "$compose_file" down --remove-orphans || true
    
    # Limpar imagens antigas (opcional)
    if [[ "$env" == "production" ]]; then
        log_info "Limpando imagens antigas..."
        docker image prune -f || true
    fi
    
    # Subir novos containers
    log_info "Subindo novos containers..."
    if docker-compose -f "$compose_file" up -d --build; then
        log_success "Deploy Docker concluído com sucesso"
        return 0
    else
        log_error "Falha no deploy Docker"
        return 1
    fi
}

# Gerenciar portas automaticamente
manage_ports() {
    local env="$1"
    log_info "Gerenciando portas para ambiente: $env"
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Encontrar portas livres
    local web_port=$(find_free_port 8000)
    local db_port=$(find_free_port 5432)
    local redis_port=$(find_free_port 6379)
    
    log_info "Portas selecionadas:"
    log_info "  Web: $web_port"
    log_info "  Database: $db_port"
    log_info "  Redis: $redis_port"
    
    # Atualizar docker-compose.yml
    update_compose_ports "$compose_file" "$web_port" "$db_port" "$redis_port"
    
    # Atualizar .env
    update_env_ports "$env" "$web_port" "$db_port" "$redis_port"
    
    return 0
}

# Encontrar porta livre
find_free_port() {
    local port="$1"
    while lsof -i ":$port" &> /dev/null; do
        port=$((port + 1))
    done
    echo "$port"
}

# Atualizar portas no docker-compose
update_compose_ports() {
    local compose_file="$1"
    local web_port="$2"
    local db_port="$3"
    local redis_port="$4"
    
    # Backup do arquivo original
    cp "$compose_file" "${compose_file}.backup"
    
    # Atualizar porta do web
    sed -i.bak "s/- \"[0-9]*:8000\"/- \"$web_port:8000\"/g" "$compose_file"
    
    # Atualizar porta do database
    sed -i.bak "s/- \"[0-9]*:5432\"/- \"$db_port:5432\"/g" "$compose_file"
    
    # Atualizar porta do redis
    sed -i.bak "s/- \"[0-9]*:6379\"/- \"$redis_port:6379\"/g" "$compose_file"
    
    log_success "Portas atualizadas no $compose_file"
}

# Atualizar portas no .env
update_env_ports() {
    local env="$1"
    local web_port="$2"
    local db_port="$3"
    local redis_port="$4"
    
    local env_file=".env"
    if [[ "$env" == "development" ]]; then
        env_file=".env.dev"
    fi
    
    if [[ -f "$env_file" ]]; then
        # Atualizar ou adicionar variáveis de porta
        update_env_var "$env_file" "DJANGO_PORT" "$web_port"
        update_env_var "$env_file" "DB_PORT" "$db_port"
        update_env_var "$env_file" "REDIS_PORT" "$redis_port"
        
        log_success "Portas atualizadas no $env_file"
    fi
}

# Atualizar variável no .env
update_env_var() {
    local env_file="$1"
    local var_name="$2"
    local var_value="$3"
    
    if grep -q "^${var_name}=" "$env_file"; then
        # Atualizar variável existente
        sed -i.bak "s/^${var_name}=.*/${var_name}=$var_value/" "$env_file"
    else
        # Adicionar nova variável
        echo "${var_name}=$var_value" >> "$env_file"
    fi
}

# Executar comandos Django no container
run_django_commands() {
    local env="$1"
    log_info "Executando comandos Django..."
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Migrations
    log_info "Executando migrations..."
    if ! docker-compose -f "$compose_file" exec -T web python manage.py migrate; then
        log_error "Falha ao executar migrations"
        return 1
    fi
    
    # Collect static (apenas em staging/production)
    if [[ "$env" != "development" ]]; then
        log_info "Coletando arquivos estáticos..."
        if ! docker-compose -f "$compose_file" exec -T web python manage.py collectstatic --noinput; then
            log_error "Falha ao coletar arquivos estáticos"
            return 1
        fi
    fi
    
    # Verificar se é primeira instalação
    if [[ -f .first_install ]]; then
        log_info "Primeira instalação detectada!"
        log_info "Inicializando módulos básicos..."
        
        if ! docker-compose -f "$compose_file" exec -T web python manage.py shell -c "
from apps.config.models.app_module_config import AppModuleConfiguration
AppModuleConfiguration.initialize_core_modules()
print('Módulos básicos inicializados com sucesso!')
"; then
            log_error "Falha ao inicializar módulos"
            return 1
        fi
        
        log_success "Sistema pronto para configuração pós-deploy!"
    else
        log_info "Instalação normal detectada"
        # Inicializar módulos normalmente
        log_info "Inicializando módulos..."
        if ! docker-compose -f "$compose_file" exec -T web python manage.py shell -c "
from apps.config.models.app_module_config import AppModuleConfiguration
AppModuleConfiguration.initialize_core_modules()
print('Módulos inicializados com sucesso!')
"; then
            log_error "Falha ao inicializar módulos"
            return 1
        fi
    fi
    
    log_success "Comandos Django executados com sucesso"
    return 0
}

# Health check dos containers
check_container_health() {
    local env="$1"
    log_info "Verificando saúde dos containers..."
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Aguardar containers inicializarem
    sleep 10
    
    # Verificar status dos containers
    local containers_status
    containers_status=$(docker-compose -f "$compose_file" ps --format "table {{.Name}}\t{{.Status}}")
    
    log_info "Status dos containers:"
    echo "$containers_status"
    
    # Verificar se todos os containers estão rodando
    local running_containers
    running_containers=$(docker-compose -f "$compose_file" ps -q | wc -l)
    local total_containers
    total_containers=$(docker-compose -f "$compose_file" config --services | wc -l)
    
    if [[ $running_containers -eq $total_containers ]]; then
        log_success "Todos os containers estão rodando"
        return 0
    else
        log_error "Alguns containers não estão rodando"
        return 1
    fi
}

# Limpeza de recursos Docker
cleanup_docker() {
    log_info "Limpando recursos Docker..."
    
    # Limpar imagens não utilizadas
    docker image prune -f || true
    
    # Limpar containers parados
    docker container prune -f || true
    
    # Limpar volumes não utilizados
    docker volume prune -f || true
    
    # Limpar redes não utilizadas
    docker network prune -f || true
    
    log_success "Limpeza Docker concluída"
}

# Backup de volumes Docker
backup_docker_volumes() {
    local env="$1"
    local backup_dir="backups/docker"
    
    log_info "Criando backup dos volumes Docker..."
    
    # Criar diretório de backup
    mkdir -p "$backup_dir"
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Obter volumes do docker-compose
    local volumes
    volumes=$(docker-compose -f "$compose_file" config --volumes)
    
    for volume in $volumes; do
        local backup_file="${backup_dir}/${volume}_$(date +%Y%m%d_%H%M%S).tar"
        
        log_info "Backup do volume: $volume"
        
        if docker run --rm -v "$volume":/data -v "$(pwd)/$backup_dir":/backup alpine tar czf "/backup/$(basename "$backup_file")" -C /data .; then
            log_success "Backup criado: $backup_file"
        else
            log_error "Falha no backup do volume: $volume"
        fi
    done
}

# Restaurar volumes Docker
restore_docker_volumes() {
    local env="$1"
    local backup_file="$2"
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Arquivo de backup não encontrado: $backup_file"
        return 1
    fi
    
    log_info "Restaurando volume Docker: $backup_file"
    
    # Extrair nome do volume do arquivo de backup
    local volume_name
    volume_name=$(basename "$backup_file" | sed 's/_.*\.tar$//')
    
    # Parar containers
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    docker-compose -f "$compose_file" down
    
    # Restaurar volume
    if docker run --rm -v "$volume_name":/data -v "$(pwd)/$(dirname "$backup_file")":/backup alpine tar xzf "/backup/$(basename "$backup_file")" -C /data; then
        log_success "Volume restaurado: $volume_name"
        return 0
    else
        log_error "Falha na restauração do volume: $volume_name"
        return 1
    fi
}

# Monitorar recursos Docker
monitor_docker_resources() {
    log_info "Monitorando recursos Docker..."
    
    # Estatísticas dos containers
    log_info "Estatísticas dos containers:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    # Uso de disco
    log_info "Uso de disco Docker:"
    docker system df
    
    # Volumes
    log_info "Volumes Docker:"
    docker volume ls --format "table {{.Name}}\t{{.Driver}}\t{{.Size}}"
}

# Logs dos containers
get_docker_logs() {
    local env="$1"
    local service="$2"
    local lines="${3:-100}"
    
    # Determinar arquivo compose
    local compose_file="docker-compose.yml"
    if [[ "$env" == "development" ]]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    if [[ -n "$service" ]]; then
        log_info "Logs do serviço: $service"
        docker-compose -f "$compose_file" logs --tail="$lines" "$service"
    else
        log_info "Logs de todos os serviços:"
        docker-compose -f "$compose_file" logs --tail="$lines"
    fi
} 