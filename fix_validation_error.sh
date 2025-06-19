#!/bin/bash

# Script para corrigir erro de validação do docker-compose.yml
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

log_section "🔧 Correção de Erro de Validação Docker Compose"

# 1. Verificar se estamos no diretório correto
if [[ ! -f "docker-compose.yml" ]]; then
    log_error "docker-compose.yml não encontrado no diretório atual"
    log_info "Certifique-se de estar no diretório do projeto FireFlies"
    exit 1
fi

log_success "docker-compose.yml encontrado"

# 2. Verificar permissões do arquivo
log_info "Verificando permissões do docker-compose.yml..."
ls -la docker-compose.yml

# 3. Verificar codificação do arquivo
log_info "Verificando codificação do arquivo..."
if command -v file &> /dev/null; then
    file docker-compose.yml
else
    log_warning "Comando 'file' não disponível, pulando verificação de codificação"
fi

# 4. Verificar se há caracteres especiais
log_info "Verificando caracteres especiais..."
if grep -q $'\r' docker-compose.yml; then
    log_warning "Arquivo contém caracteres de retorno de carro (Windows line endings)"
    log_info "Convertendo para Unix line endings..."
    dos2unix docker-compose.yml 2>/dev/null || sed -i 's/\r$//' docker-compose.yml
    log_success "Line endings convertidos"
else
    log_success "Line endings estão corretos"
fi

# 5. Verificar sintaxe com docker-compose
log_info "Testando sintaxe do docker-compose.yml..."
if docker-compose config > /dev/null 2>&1; then
    log_success "Sintaxe do docker-compose.yml está válida"
else
    log_error "Erro de sintaxe detectado"
    log_info "Executando validação detalhada..."
    docker-compose config
    exit 1
fi

# 6. Verificar se há variáveis de ambiente não definidas
log_info "Verificando variáveis de ambiente..."
if [[ -f ".env" ]]; then
    log_success "Arquivo .env encontrado"
    
    # Verificar se as variáveis necessárias estão definidas
    required_vars=("DB_NAME" "DB_USER" "DB_PASSWORD" "SECRET_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_warning "Variáveis faltando no .env: ${missing_vars[*]}"
    else
        log_success "Todas as variáveis necessárias estão definidas"
    fi
else
    log_warning "Arquivo .env não encontrado"
fi

# 7. Verificar se há conflitos de porta
log_info "Verificando portas em uso..."
ports_to_check=(80 443 8000 5432 6379)
occupied_ports=()

for port in "${ports_to_check[@]}"; do
    if lsof -i ":$port" &> /dev/null; then
        occupied_ports+=("$port")
    fi
done

if [[ ${#occupied_ports[@]} -gt 0 ]]; then
    log_warning "Portas ocupadas: ${occupied_ports[*]}"
    log_info "Isso pode causar problemas no deploy"
else
    log_success "Todas as portas necessárias estão livres"
fi

# 8. Verificar se o Docker está funcionando
log_info "Verificando Docker..."
if ! docker info &> /dev/null; then
    log_error "Docker não está funcionando ou não está acessível"
    exit 1
fi

if ! docker-compose version &> /dev/null; then
    log_error "Docker Compose não está disponível"
    exit 1
fi

log_success "Docker e Docker Compose estão funcionando"

# 9. Teste final de validação
log_info "Executando teste final de validação..."
if docker-compose config &> /dev/null; then
    log_success "✅ Validação final: SUCESSO"
    log_info "O docker-compose.yml está válido e pronto para uso"
else
    log_error "❌ Validação final: FALHA"
    log_info "Executando validação com output completo para debug..."
    docker-compose config
    exit 1
fi

log_section "🎯 Resumo da Correção"
log_success "Todas as verificações passaram"
log_info "O arquivo docker-compose.yml está válido"
log_info "Você pode tentar executar o deploy novamente"

# 10. Sugestões adicionais
log_section "💡 Sugestões"
log_info "Se o problema persistir, tente:"
log_info "1. docker-compose down --remove-orphans"
log_info "2. docker system prune -f"
log_info "3. Executar o deploy novamente"

exit 0 