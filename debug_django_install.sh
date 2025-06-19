#!/bin/bash

# Script para debugar a instalação do Django
# Executar no servidor Linux para investigar o problema

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

log_section "Debugando Instalacao do Django"

# 1. Verificar arquivos de requirements
log_info "Verificando arquivos de requirements..."
if [[ -f "requirements.txt" ]]; then
    log_success "requirements.txt encontrado"
    log_info "Conteudo do requirements.txt:"
    cat requirements.txt
else
    log_error "requirements.txt nao encontrado"
    exit 1
fi

echo ""
if [[ -f "requirements-prod.txt" ]]; then
    log_success "requirements-prod.txt encontrado"
    log_info "Conteudo do requirements-prod.txt:"
    cat requirements-prod.txt
else
    log_error "requirements-prod.txt nao encontrado"
    exit 1
fi

# 2. Testar instalação manual em container temporário
log_section "Testando Instalacao Manual"

log_info "Criando container temporario para teste..."
docker run --rm -it -v $(pwd):/app ubuntu:22.04 bash -c "
    echo 'Atualizando sistema...'
    apt-get update
    
    echo 'Instalando Python...'
    apt-get install -y python3.11 python3.11-dev python3-pip build-essential
    
    echo 'Criando link simbólico...'
    ln -s /usr/bin/python3.11 /usr/bin/python
    
    echo 'Navegando para /app...'
    cd /app
    
    echo 'Verificando arquivos...'
    ls -la requirements*.txt
    
    echo 'Instalando dependências...'
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    
    echo 'Verificando Django...'
    python -c 'import django; print(\"Django version:\", django.get_version())'
    
    echo 'Listando pacotes instalados...'
    pip3 list | grep -i django
"

# 3. Verificar se o problema está no requirements-prod.txt
log_section "Testando Requirements Separadamente"

log_info "Testando apenas requirements.txt..."
docker run --rm -it -v $(pwd):/app ubuntu:22.04 bash -c "
    apt-get update
    apt-get install -y python3.11 python3.11-dev python3-pip build-essential
    ln -s /usr/bin/python3.11 /usr/bin/python
    cd /app
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    python -c 'import django; print(\"Django OK\")'
"

# 4. Verificar se o problema está no Dockerfile
log_section "Verificando Dockerfile"

if [[ -f "Dockerfile" ]]; then
    log_success "Dockerfile encontrado"
    log_info "Conteudo do Dockerfile:"
    cat Dockerfile
else
    log_error "Dockerfile nao encontrado"
    exit 1
fi

# 5. Testar build com mais verbosidade
log_section "Testando Build Verboso"

log_info "Fazendo build com mais verbosidade..."
docker-compose build --no-cache --progress=plain web

# 6. Verificar o que está dentro do container
log_section "Verificando Container"

log_info "Verificando conteudo do container..."
docker-compose run --rm web bash -c "
    echo 'Python version:'
    python --version
    
    echo 'Pip version:'
    pip --version
    
    echo 'Diretório atual:'
    pwd
    
    echo 'Arquivos no diretório:'
    ls -la
    
    echo 'Requirements instalados:'
    pip list
    
    echo 'Tentando importar Django:'
    python -c 'import django; print(\"Django version:\", django.get_version())' || echo 'Falha ao importar Django'
"

log_section "Debug Concluido"
log_info "Verifique a saída acima para identificar o problema" 