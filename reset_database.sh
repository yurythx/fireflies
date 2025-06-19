#!/bin/bash

# Script para resetar o banco de dados PostgreSQL
# Use com cuidado - isso apaga todos os dados!

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

# Função principal
main() {
    log_info "🗄️  Resetando Banco de Dados PostgreSQL - FireFlies"
    log_info "=================================================="
    
    # Verificar se está no diretório correto
    if [[ ! -f "docker-compose.yml" ]]; then
        log_error "Execute este script no diretório raiz do projeto"
        exit 1
    fi
    
    # Confirmar ação
    log_warning "⚠️  ATENÇÃO: Isso irá apagar todos os dados do banco!"
    log_warning "   - Todos os dados serão perdidos"
    log_warning "   - O banco será recriado do zero"
    echo ""
    read -p "Tem certeza que deseja continuar? (digite 'sim' para confirmar): " confirm
    
    if [[ "$confirm" != "sim" ]]; then
        log_info "Operação cancelada pelo usuário"
        exit 0
    fi
    
    log_info ""
    log_info "🛑 Parando containers..."
    
    # Parar containers
    docker-compose down
    
    log_info "🗑️  Removendo volume do PostgreSQL..."
    
    # Remover volume do PostgreSQL
    docker volume rm fireflies_postgres_data 2>/dev/null || true
    
    log_info "🧹 Limpando containers e imagens não utilizadas..."
    
    # Limpar containers parados
    docker container prune -f
    
    # Limpar imagens não utilizadas
    docker image prune -f
    
    log_info "🚀 Iniciando containers com banco limpo..."
    
    # Subir containers novamente
    docker-compose up -d
    
    log_info "⏳ Aguardando banco de dados inicializar..."
    
    # Aguardar banco estar pronto
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose exec -T db pg_isready -U fireflies_user >/dev/null 2>&1; then
            log_success "Banco de dados está pronto!"
            break
        fi
        
        log_info "Tentativa $attempt/$max_attempts - Aguardando..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_error "Timeout aguardando banco de dados"
        exit 1
    fi
    
    log_info "🔧 Executando migrations..."
    
    # Executar migrations
    docker-compose exec -T web python manage.py migrate
    
    log_info "👤 Criando superusuário..."
    
    # Criar superusuário
    docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@fireflies.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"
    
    log_info "📊 Verificando status dos containers..."
    
    # Verificar status
    docker-compose ps
    
    log_success ""
    log_success "🎉 Banco de dados resetado com sucesso!"
    log_success ""
    log_success "📋 Informações de acesso:"
    log_success "   URL: http://localhost:8000"
    log_success "   Admin: http://localhost:8000/admin"
    log_success "   Usuário: admin"
    log_success "   Senha: admin123"
    log_success ""
    log_success "🔍 Para ver logs: docker-compose logs -f"
    log_success "🛑 Para parar: docker-compose down"
}

# Executar função principal
main 