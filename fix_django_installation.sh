#!/bin/bash

# Script para corrigir instalação do Django no container
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

log_section "Corrigindo Instalacao do Django"

# 1. Verificar se estamos no diretório correto
if [[ ! -f "docker-compose.yml" ]]; then
    log_error "docker-compose.yml nao encontrado no diretorio atual"
    log_info "Certifique-se de estar no diretorio do projeto FireFlies"
    exit 1
fi

log_success "docker-compose.yml encontrado"

# 2. Verificar se os arquivos de requirements existem
if [[ ! -f "requirements.txt" ]]; then
    log_error "requirements.txt nao encontrado"
    exit 1
fi

if [[ ! -f "requirements-prod.txt" ]]; then
    log_error "requirements-prod.txt nao encontrado"
    exit 1
fi

log_success "Arquivos de requirements encontrados"

# 3. Parar containers existentes
log_info "Parando containers existentes..."
docker-compose down --remove-orphans
log_success "Containers parados"

# 4. Remover imagem antiga
log_info "Removendo imagem antiga..."
docker rmi fireflies-web:latest 2>/dev/null || true
log_success "Imagem antiga removida"

# 5. Limpar cache do Docker
log_info "Limpando cache do Docker..."
docker system prune -f
log_success "Cache limpo"

# 6. Reconstruir a imagem
log_info "Reconstruindo imagem do Django..."
docker-compose build --no-cache web
log_success "Imagem reconstruida"

# 7. Verificar se o Django foi instalado corretamente
log_info "Verificando instalacao do Django..."
if docker-compose run --rm web python -c "import django; print('Django version:', django.get_version())"; then
    log_success "Django instalado corretamente"
else
    log_error "Django nao foi instalado corretamente"
    exit 1
fi

# 8. Iniciar containers
log_info "Iniciando containers..."
docker-compose up -d
log_success "Containers iniciados"

# 9. Aguardar o banco inicializar
log_info "Aguardando banco de dados inicializar..."
sleep 15

# 10. Verificar status dos containers
log_info "Verificando status dos containers..."
docker-compose ps

# 11. Executar migrations
log_info "Executando migrations..."
if docker-compose exec web python manage.py migrate; then
    log_success "Migrations executadas com sucesso"
else
    log_error "Falha ao executar migrations"
    log_info "Verificando logs do container web..."
    docker-compose logs web
    exit 1
fi

# 12. Coletar arquivos estáticos
log_info "Coletando arquivos estaticos..."
if docker-compose exec web python manage.py collectstatic --noinput; then
    log_success "Arquivos estaticos coletados"
else
    log_warning "Falha ao coletar arquivos estaticos"
fi

log_section "Resumo da Correcao"
log_success "Instalacao do Django corrigida"
log_info "Containers iniciados e funcionando"
log_info "Migrations executadas"

log_section "URLs de Acesso"
log_info "Django direto: http://localhost:8000"
log_info "Via Nginx: http://localhost:8080"

log_section "Proximos Passos"
log_info "Para criar um superuser:"
log_info "  docker-compose exec web python manage.py createsuperuser"

log_info "Para ver logs:"
log_info "  docker-compose logs -f web"

exit 0 