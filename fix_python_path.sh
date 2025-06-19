#!/bin/bash

# Script para corrigir problemas de Python path e ambiente
# Executar no servidor Linux para resolver problema de importação do Django

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

log_section "Corrigindo Problemas de Python Path"

# 1. Verificar se estamos no diretório correto
if [[ ! -f "docker-compose.yml" ]]; then
    log_error "docker-compose.yml nao encontrado no diretorio atual"
    log_info "Certifique-se de estar no diretorio do projeto FireFlies"
    exit 1
fi

log_success "docker-compose.yml encontrado"

# 2. Parar containers existentes
log_info "Parando containers existentes..."
docker-compose down --remove-orphans
log_success "Containers parados"

# 3. Remover imagem antiga
log_info "Removendo imagem antiga..."
docker rmi fireflies-web:latest 2>/dev/null || true
log_success "Imagem antiga removida"

# 4. Criar Dockerfile corrigido
log_info "Criando Dockerfile corrigido..."
cat > Dockerfile.fixed << 'EOF'
# Imagem base com Python 3.11
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar as dependências do projeto
COPY requirements.txt requirements-prod.txt ./

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements-prod.txt

# Copiar o restante do código
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Verificar instalação do Django
RUN python -c "import django; print('Django version:', django.get_version())"

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF

log_success "Dockerfile corrigido criado"

# 5. Atualizar docker-compose.yml para usar o novo Dockerfile
log_info "Atualizando docker-compose.yml..."
sed -i 's/build: \./build:\n      dockerfile: Dockerfile.fixed/' docker-compose.yml
log_success "docker-compose.yml atualizado"

# 6. Reconstruir a imagem
log_info "Reconstruindo imagem com Dockerfile corrigido..."
docker-compose build --no-cache web
log_success "Imagem reconstruida"

# 7. Verificar se o Django foi instalado corretamente
log_info "Verificando instalacao do Django..."
if docker-compose run --rm web python -c "import django; print('Django version:', django.get_version())"; then
    log_success "Django instalado corretamente"
else
    log_error "Django ainda nao foi instalado corretamente"
    log_info "Verificando logs de build..."
    docker-compose build --no-cache --progress=plain web
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
log_success "Problemas de Python path corrigidos"
log_info "Django instalado e funcionando"
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

# 13. Limpeza
log_info "Removendo arquivo temporario..."
rm -f Dockerfile.fixed
log_success "Limpeza concluida"

exit 0 