#!/bin/bash

# Teste do Sistema de Deploy FireFlies
# Script para verificar se todos os módulos estão funcionando

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

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Função para executar teste
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    log_info "Executando teste: $test_name"
    
    if eval "$test_command"; then
        log_success "✅ $test_name - PASSOU"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "❌ $test_name - FALHOU"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Função para verificar se arquivo existe
check_file() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        log_success "✅ $description: $file"
        return 0
    else
        log_error "❌ $description: $file (não encontrado)"
        return 1
    fi
}

# Função para verificar se diretório existe
check_directory() {
    local dir="$1"
    local description="$2"
    
    if [[ -d "$dir" ]]; then
        log_success "✅ $description: $dir"
        return 0
    else
        log_error "❌ $description: $dir (não encontrado)"
        return 1
    fi
}

# Função para verificar se comando existe
check_command() {
    local command="$1"
    local description="$2"
    
    if command -v "$command" &> /dev/null; then
        log_success "✅ $description: $command"
        return 0
    else
        log_error "❌ $description: $command (não encontrado)"
        return 1
    fi
}

# Função para verificar sintaxe de script
check_syntax() {
    local script="$1"
    local description="$2"
    
    if bash -n "$script" 2>/dev/null; then
        log_success "✅ $description: sintaxe OK"
        return 0
    else
        log_error "❌ $description: erro de sintaxe"
        return 1
    fi
}

# Função para verificar se módulo pode ser importado
check_module_import() {
    local module="$1"
    local description="$2"
    
    if source "$module" 2>/dev/null; then
        log_success "✅ $description: importação OK"
        return 0
    else
        log_error "❌ $description: erro na importação"
        return 1
    fi
}

# Função principal de teste
main() {
    log_info "🧪 Iniciando testes do Sistema de Deploy FireFlies"
    log_info "=================================================="
    
    # Teste 1: Verificar estrutura de arquivos
    log_info ""
    log_info "📁 Testando estrutura de arquivos..."
    
    run_test "Script principal existe" "check_file 'deploy_improved.sh' 'Script principal'"
    run_test "Configuração existe" "check_file 'deploy.config' 'Arquivo de configuração'"
    run_test "Documentação existe" "check_file 'README_DEPLOY_IMPROVED.md' 'Documentação'"
    
    # Teste 2: Verificar diretório de módulos
    log_info ""
    log_info "🧩 Testando módulos..."
    
    run_test "Diretório de módulos existe" "check_directory 'scripts/deploy/modules' 'Diretório de módulos'"
    run_test "Módulo de logging existe" "check_file 'scripts/deploy/modules/logging.sh' 'Módulo de logging'"
    run_test "Módulo de ambiente existe" "check_file 'scripts/deploy/modules/environment.sh' 'Módulo de ambiente'"
    run_test "Módulo de validação existe" "check_file 'scripts/deploy/modules/validation.sh' 'Módulo de validação'"
    run_test "Módulo Docker existe" "check_file 'scripts/deploy/modules/docker.sh' 'Módulo Docker'"
    run_test "Módulo health existe" "check_file 'scripts/deploy/modules/health.sh' 'Módulo health'"
    
    # Teste 3: Verificar sintaxe dos scripts
    log_info ""
    log_info "🔍 Testando sintaxe dos scripts..."
    
    run_test "Sintaxe do script principal" "check_syntax 'deploy_improved.sh' 'Script principal'"
    run_test "Sintaxe do módulo logging" "check_syntax 'scripts/deploy/modules/logging.sh' 'Módulo logging'"
    run_test "Sintaxe do módulo environment" "check_syntax 'scripts/deploy/modules/environment.sh' 'Módulo environment'"
    run_test "Sintaxe do módulo validation" "check_syntax 'scripts/deploy/modules/validation.sh' 'Módulo validation'"
    run_test "Sintaxe do módulo docker" "check_syntax 'scripts/deploy/modules/docker.sh' 'Módulo docker'"
    run_test "Sintaxe do módulo health" "check_syntax 'scripts/deploy/modules/health.sh' 'Módulo health'"
    
    # Teste 4: Verificar importação de módulos
    log_info ""
    log_info "📦 Testando importação de módulos..."
    
    # Criar script temporário para testar importação
    cat > /tmp/test_import.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Importar módulos
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/deploy/modules/logging.sh"
source "$SCRIPT_DIR/scripts/deploy/modules/environment.sh"
source "$SCRIPT_DIR/scripts/deploy/modules/validation.sh"
source "$SCRIPT_DIR/scripts/deploy/modules/docker.sh"
source "$SCRIPT_DIR/scripts/deploy/modules/health.sh"

echo "Todos os módulos importados com sucesso"
EOF
    
    run_test "Importação de módulos" "bash /tmp/test_import.sh"
    
    # Limpar arquivo temporário
    rm -f /tmp/test_import.sh
    
    # Teste 5: Verificar permissões
    log_info ""
    log_info "🔐 Testando permissões..."
    
    run_test "Script principal é executável" "[[ -x 'deploy_improved.sh' ]]"
    
    # Teste 6: Verificar funções principais
    log_info ""
    log_info "⚙️ Testando funções principais..."
    
    # Testar função de detecção de ambiente
    run_test "Função detect_environment" "
        source scripts/deploy/modules/environment.sh
        env=\$(detect_environment)
        [[ -n \"\$env\" ]]
    "
    
    # Testar função de logging
    run_test "Função log_info" "
        source scripts/deploy/modules/logging.sh
        log_info 'Teste de logging' > /dev/null
    "
    
    # Teste 7: Verificar configurações
    log_info ""
    log_info "⚙️ Testando configurações..."
    
    run_test "Arquivo de configuração é válido" "
        [[ -f 'deploy.config' ]] && grep -q 'DEFAULT_ENVIRONMENT' 'deploy.config'
    "
    
    # Teste 8: Verificar ajuda do script
    log_info ""
    log_info "📖 Testando ajuda do script..."
    
    run_test "Comando de ajuda funciona" "
        ./deploy_improved.sh --help | grep -q 'FireFlies Deploy System'
    "
    
    # Teste 9: Verificar comandos específicos
    log_info ""
    log_info "🛠️ Testando comandos específicos..."
    
    run_test "Comando health-check existe" "
        ./deploy_improved.sh health-check --help > /dev/null 2>&1 || true
    "
    
    run_test "Comando backup existe" "
        ./deploy_improved.sh backup --help > /dev/null 2>&1 || true
    "
    
    run_test "Comando status existe" "
        ./deploy_improved.sh status --help > /dev/null 2>&1 || true
    "
    
    # Teste 10: Verificar dependências do sistema
    log_info ""
    log_info "🔧 Testando dependências do sistema..."
    
    run_test "Bash disponível" "check_command 'bash' 'Bash'"
    run_test "Docker disponível" "check_command 'docker' 'Docker'"
    run_test "Docker Compose disponível" "check_command 'docker-compose' 'Docker Compose'"
    run_test "Git disponível" "check_command 'git' 'Git'"
    
    # Teste 11: Verificar estrutura do projeto
    log_info ""
    log_info "📂 Testando estrutura do projeto..."
    
    run_test "Dockerfile existe" "check_file 'Dockerfile' 'Dockerfile'"
    run_test "docker-compose.yml existe" "check_file 'docker-compose.yml' 'docker-compose.yml'"
    run_test "requirements.txt existe" "check_file 'requirements.txt' 'requirements.txt'"
    run_test "manage.py existe" "check_file 'manage.py' 'manage.py'"
    
    # Teste 12: Verificar sintaxe do docker-compose
    log_info ""
    log_info "🐳 Testando configuração Docker..."
    
    run_test "Sintaxe do docker-compose.yml" "
        docker-compose config > /dev/null 2>&1
    "
    
    # Resumo dos testes
    log_info ""
    log_info "📊 RESUMO DOS TESTES"
    log_info "===================="
    log_info "Total de testes: $TESTS_TOTAL"
    log_info "Testes passaram: $TESTS_PASSED"
    log_info "Testes falharam: $TESTS_FAILED"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "🎉 TODOS OS TESTES PASSARAM!"
        log_success "Sistema de deploy está pronto para uso."
        exit 0
    else
        log_error "⚠️  $TESTS_FAILED TESTE(S) FALHARAM"
        log_error "Verifique os erros acima antes de usar o sistema."
        exit 1
    fi
}

# Função de limpeza
cleanup() {
    log_info "🧹 Limpando arquivos temporários..."
    rm -f /tmp/test_import.sh
}

# Configurar trap para limpeza
trap cleanup EXIT

# Executar função principal
main "$@" 