#!/bin/bash

# Script para detectar e corrigir conflitos de porta automaticamente
# Executar no servidor Linux onde o deploy está falhando

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de logging
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

log_section() {
    echo -e "\n${BLUE}==================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==================================${NC}"
}

# Função para encontrar porta livre
find_free_port() {
    local start_port=$1
    local port=$start_port
    
    while netstat -tuln | grep -q ":$port "; do
        port=$((port + 1))
    done
    
    echo $port
}

log_section "Detectando e Corrigindo Conflitos de Porta"

# 1. Verificar se estamos no diretório correto
if [[ ! -f "docker-compose.yml" ]]; then
    log_error "docker-compose.yml nao encontrado no diretorio atual"
    log_info "Certifique-se de estar no diretorio do projeto FireFlies"
    exit 1
fi

log_success "docker-compose.yml encontrado"

# 2. Detectar portas disponíveis
log_info "Detectando portas disponiveis..."
WEB_PORT=$(find_free_port 8000)
DB_PORT=$(find_free_port 5432)
REDIS_PORT=$(find_free_port 6379)
NGINX_PORT=$(find_free_port 80)
NGINX_SSL_PORT=$(find_free_port 443)

log_success "Portas detectadas:"
log_info "  Web: $WEB_PORT (Django)"
log_info "  DB: $DB_PORT (PostgreSQL)"
log_info "  Redis: $REDIS_PORT (Cache)"
log_info "  Nginx: $NGINX_PORT (HTTP)"
log_info "  Nginx SSL: $NGINX_SSL_PORT (HTTPS)"

# 3. Verificar se as portas padrão estão ocupadas
log_info "Verificando portas padrao..."
occupied_ports=()
for port in 8000 5432 6379 80 443; do
    if netstat -tuln | grep -q ":$port "; then
        occupied_ports+=("$port")
    fi
done

if [[ ${#occupied_ports[@]} -gt 0 ]]; then
    log_warning "Portas ocupadas: ${occupied_ports[*]}"
    log_info "Usando portas alternativas detectadas"
else
    log_success "Todas as portas padrao estao livres"
fi

# 4. Fazer backup do docker-compose.yml atual
log_info "Fazendo backup do docker-compose.yml..."
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
log_success "Backup criado"

# 5. Atualizar docker-compose.yml com portas detectadas
log_info "Atualizando docker-compose.yml com portas detectadas..."

# Atualizar portas no docker-compose.yml
sed -i "s|      - \"8000:8000\"|      - \"$WEB_PORT:8000\"|" docker-compose.yml
sed -i "s|      - \"5432:5432\"|      - \"$DB_PORT:5432\"|" docker-compose.yml
sed -i "s|      - \"6379:6379\"|      - \"$REDIS_PORT:6379\"|" docker-compose.yml
sed -i "s|      - \"80:80\"|      - \"$NGINX_PORT:80\"|" docker-compose.yml
sed -i "s|      - \"443:443\"|      - \"$NGINX_SSL_PORT:443\"|" docker-compose.yml

log_success "docker-compose.yml atualizado com portas: $WEB_PORT, $DB_PORT, $REDIS_PORT, $NGINX_PORT, $NGINX_SSL_PORT"

# 6. Atualizar arquivo .env com as portas detectadas
if [[ -f .env ]]; then
    log_info "Atualizando arquivo .env com portas detectadas..."
    
    # Atualizar ou adicionar configurações de portas
    if grep -q "^DJANGO_PORT=" .env; then
        sed -i "s|^DJANGO_PORT=.*|DJANGO_PORT=$WEB_PORT|" .env
    else
        echo "DJANGO_PORT=$WEB_PORT" >> .env
    fi
    
    if grep -q "^POSTGRES_PORT=" .env; then
        sed -i "s|^POSTGRES_PORT=.*|POSTGRES_PORT=$DB_PORT|" .env
    else
        echo "POSTGRES_PORT=$DB_PORT" >> .env
    fi
    
    if grep -q "^REDIS_PORT=" .env; then
        sed -i "s|^REDIS_PORT=.*|REDIS_PORT=$REDIS_PORT|" .env
    else
        echo "REDIS_PORT=$REDIS_PORT" >> .env
    fi
    
    if grep -q "^NGINX_PORT=" .env; then
        sed -i "s|^NGINX_PORT=.*|NGINX_PORT=$NGINX_PORT|" .env
    else
        echo "NGINX_PORT=$NGINX_PORT" >> .env
    fi
    
    if grep -q "^NGINX_SSL_PORT=" .env; then
        sed -i "s|^NGINX_SSL_PORT=.*|NGINX_SSL_PORT=$NGINX_SSL_PORT|" .env
    else
        echo "NGINX_SSL_PORT=$NGINX_SSL_PORT" >> .env
    fi
    
    log_success "Arquivo .env atualizado"
else
    log_warning "Arquivo .env nao encontrado"
fi

# 7. Validar o docker-compose.yml atualizado
log_info "Validando docker-compose.yml atualizado..."
if docker-compose config > /dev/null 2>&1; then
    log_success "docker-compose.yml esta valido"
else
    log_error "Erro de sintaxe no docker-compose.yml"
    log_info "Executando validacao detalhada..."
    docker-compose config
    exit 1
fi

# 8. Parar containers existentes se houver
log_info "Parando containers existentes..."
docker-compose down --remove-orphans 2>/dev/null || true
log_success "Containers parados"

# 9. Limpar recursos Docker não utilizados
log_info "Limpando recursos Docker nao utilizados..."
docker system prune -f > /dev/null 2>&1 || true
log_success "Limpeza concluida"

log_section "Resumo da Correcao"
log_success "Conflitos de porta corrigidos automaticamente"
log_info "Portas configuradas:"
log_info "  Django: http://localhost:$WEB_PORT"
log_info "  PostgreSQL: localhost:$DB_PORT"
log_info "  Redis: localhost:$REDIS_PORT"
log_info "  Nginx: http://localhost:$NGINX_PORT"
log_info "  Nginx SSL: https://localhost:$NGINX_SSL_PORT"

log_section "Proximos Passos"
log_info "Agora voce pode executar o deploy:"
log_info "  ./deploy_improved.sh"

log_info "Ou testar manualmente:"
log_info "  docker-compose up -d"

exit 0 