#!/bin/bash

# Script de Limpeza Profunda - FireFlies
# Remove arquivos não utilizados do projeto

set -euo pipefail

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Contadores
FILES_REMOVED=0
FILES_KEPT=0
TOTAL_SIZE_REMOVED=0

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

# Função para calcular tamanho de arquivo
get_file_size() {
    local file="$1"
    if [[ -f "$file" ]]; then
        du -b "$file" | cut -f1
    else
        echo "0"
    fi
}

# Função para remover arquivo com backup
remove_file() {
    local file="$1"
    local reason="$2"
    
    if [[ -f "$file" ]]; then
        local size
        size=$(get_file_size "$file")
        
        # Criar backup
        local backup_dir="backups/cleanup/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        # Mover para backup
        mv "$file" "$backup_dir/"
        
        log_success "Removido: $file ($reason) - Backup em: $backup_dir/"
        FILES_REMOVED=$((FILES_REMOVED + 1))
        TOTAL_SIZE_REMOVED=$((TOTAL_SIZE_REMOVED + size))
    fi
}

# Função para remover diretório com backup
remove_directory() {
    local dir="$1"
    local reason="$2"
    
    if [[ -d "$dir" ]]; then
        # Criar backup
        local backup_dir="backups/cleanup/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        # Mover para backup
        mv "$dir" "$backup_dir/"
        
        log_success "Removido: $dir ($reason) - Backup em: $backup_dir/"
        FILES_REMOVED=$((FILES_REMOVED + 1))
    fi
}

# Função para verificar se arquivo é usado
check_file_usage() {
    local file="$1"
    local search_pattern="$2"
    
    if grep -r "$search_pattern" . --exclude-dir=.git --exclude-dir=backups --exclude-dir=node_modules --exclude-dir=__pycache__ --exclude="*.pyc" --exclude="*.log" &> /dev/null; then
        return 0  # Arquivo é usado
    else
        return 1  # Arquivo não é usado
    fi
}

# Função principal de limpeza
main() {
    log_info "🧹 Iniciando limpeza profunda do projeto FireFlies"
    log_info "=================================================="
    
    # Criar diretório de backup
    mkdir -p "backups/cleanup/$(date +%Y%m%d_%H%M%S)"
    
    log_info ""
    log_info "📁 1. Removendo scripts de deploy antigos..."
    
    # Scripts de deploy antigos (substituídos pelo deploy_improved.sh)
    if [[ -f "deploy.sh" ]]; then
        remove_file "deploy.sh" "Substituído por deploy_improved.sh"
    fi
    
    if [[ -f "deploy.ps1" ]]; then
        remove_file "deploy.ps1" "Substituído por deploy_improved.sh"
    fi
    
    log_info ""
    log_info "🐍 2. Removendo scripts Python não utilizados..."
    
    # Scripts Python não utilizados
    if [[ -f "fix_articles_module.py" ]]; then
        remove_file "fix_articles_module.py" "Script não utilizado"
    fi
    
    if [[ -f "verificar_artigos.py" ]]; then
        remove_file "verificar_artigos.py" "Script não utilizado"
    fi
    
    if [[ -f "corrigir_modulo_artigos.py" ]]; then
        remove_file "corrigir_modulo_artigos.py" "Script não utilizado"
    fi
    
    log_info ""
    log_info "🔧 3. Removendo scripts de instalação específicos..."
    
    # Scripts de instalação específicos (já executados)
    if [[ -f "install_ubuntu.sh" ]]; then
        remove_file "install_ubuntu.sh" "Script de instalação já executado"
    fi
    
    if [[ -f "test_network.sh" ]]; then
        remove_file "test_network.sh" "Script de teste de rede não utilizado"
    fi
    
    if [[ -f "clean_env.sh" ]]; then
        remove_file "clean_env.sh" "Script de limpeza de ambiente não utilizado"
    fi
    
    log_info ""
    log_info "📚 4. Removendo documentação duplicada/obsoleta..."
    
    # Documentação duplicada/obsoleta
    if [[ -f "README_UBUNTU.md" ]]; then
        remove_file "README_UBUNTU.md" "Documentação específica Ubuntu obsoleta"
    fi
    
    if [[ -f "MELHORIAS_UBUNTU.md" ]]; then
        remove_file "MELHORIAS_UBUNTU.md" "Documentação de melhorias Ubuntu obsoleta"
    fi
    
    if [[ -f "RESUMO_MELHORIAS.md" ]]; then
        remove_file "RESUMO_MELHORIAS.md" "Substituído por RESUMO_MELHORIAS_IMPLEMENTADAS.md"
    fi
    
    if [[ -f "DEPLOY_GUIDE.md" ]]; then
        remove_file "DEPLOY_GUIDE.md" "Guia de deploy obsoleto"
    fi
    
    if [[ -f "DETECCAO_IP.md" ]]; then
        remove_file "DETECCAO_IP.md" "Documentação de detecção de IP obsoleta"
    fi
    
    log_info ""
    log_info "🐳 5. Removendo arquivos Docker não utilizados..."
    
    # Arquivos Docker não utilizados
    if [[ -f "docker-compose.min.yml" ]]; then
        remove_file "docker-compose.min.yml" "Arquivo docker-compose mínimo não utilizado"
    fi
    
    log_info ""
    log_info "🧩 6. Removendo módulos não utilizados..."
    
    # Módulo common não utilizado
    if [[ -d "apps/common" ]]; then
        if ! check_file_usage "apps/common" "from apps.common"; then
            remove_directory "apps/common" "Módulo common não utilizado"
        else
            log_warning "Mantido: apps/common (pode estar sendo usado)"
            FILES_KEPT=$((FILES_KEPT + 1))
        fi
    fi
    
    # Módulo core não utilizado
    if [[ -d "apps/core" ]]; then
        if ! check_file_usage "apps/core" "from apps.core"; then
            remove_directory "apps/core" "Módulo core não utilizado"
        else
            log_warning "Mantido: apps/core (pode estar sendo usado)"
            FILES_KEPT=$((FILES_KEPT + 1))
        fi
    fi
    
    log_info ""
    log_info "📁 7. Removendo diretórios de testes vazios..."
    
    # Diretórios de testes vazios
    if [[ -d "tests" ]] && [[ $(find tests -type f -name "*.py" | wc -l) -eq 1 ]]; then
        # Se só tem __init__.py
        remove_directory "tests" "Diretório de testes vazio"
    fi
    
    # Verificar diretórios de testes vazios nos apps
    for app in apps/*/tests; do
        if [[ -d "$app" ]] && [[ $(find "$app" -type f -name "*.py" | wc -l) -eq 1 ]]; then
            remove_directory "$app" "Diretório de testes vazio"
        fi
    done
    
    log_info ""
    log_info "🎨 8. Removendo templates não utilizados..."
    
    # Templates não utilizados
    if [[ -f "templates/admin/base_site.html" ]]; then
        if ! check_file_usage "templates/admin/base_site.html" "base_site.html"; then
            remove_file "templates/admin/base_site.html" "Template admin não utilizado"
        else
            log_warning "Mantido: templates/admin/base_site.html (pode estar sendo usado)"
            FILES_KEPT=$((FILES_KEPT + 1))
        fi
    fi
    
    log_info ""
    log_info "📄 9. Removendo arquivos temporários..."
    
    # Arquivos temporários
    if [[ -f ".temp_db_config.json" ]]; then
        remove_file ".temp_db_config.json" "Arquivo temporário de configuração"
    fi
    
    # Manter .first_install pois é usado pelo sistema
    if [[ -f ".first_install" ]]; then
        log_info "Mantido: .first_install (usado pelo sistema de deploy)"
        FILES_KEPT=$((FILES_KEPT + 1))
    fi
    
    log_info ""
    log_info "📊 10. Limpando arquivos de configuração duplicados..."
    
    # Verificar se há arquivos de configuração duplicados
    if [[ -f "pytest.ini" ]] && [[ -f ".coveragerc" ]]; then
        # Manter ambos pois são para propósitos diferentes
        log_info "Mantidos: pytest.ini e .coveragerc (configurações de teste)"
        FILES_KEPT=$((FILES_KEPT + 2))
    fi
    
    log_info ""
    log_info "🗂️ 11. Verificando arquivos estáticos..."
    
    # Verificar se staticfiles está sendo usado
    if [[ -d "staticfiles" ]]; then
        log_info "Mantido: staticfiles/ (gerado pelo Django collectstatic)"
        FILES_KEPT=$((FILES_KEPT + 1))
    fi
    
    log_info ""
    log_info "📋 RESUMO DA LIMPEZA"
    log_info "===================="
    log_info "Arquivos removidos: $FILES_REMOVED"
    log_info "Arquivos mantidos: $FILES_KEPT"
    
    if [[ $TOTAL_SIZE_REMOVED -gt 0 ]]; then
        local size_mb
        size_mb=$(echo "scale=2; $TOTAL_SIZE_REMOVED / 1024 / 1024" | bc -l 2>/dev/null || echo "0")
        log_info "Espaço liberado: ${size_mb}MB"
    fi
    
    log_info ""
    log_info "💾 Backups salvos em: backups/cleanup/"
    log_info ""
    log_info "✅ Limpeza concluída!"
    
    # Sugestões adicionais
    log_info ""
    log_info "💡 Sugestões adicionais:"
    log_info "  • Execute: git status para ver mudanças"
    log_info "  • Execute: git add . para adicionar mudanças"
    log_info "  • Execute: git commit -m 'Cleanup: remove unused files'"
    log_info "  • Verifique: backups/cleanup/ antes de fazer commit"
}

# Função de limpeza segura (apenas lista arquivos)
dry_run() {
    log_info "🔍 Modo DRY RUN - Apenas listando arquivos que seriam removidos"
    log_info "================================================================"
    
    log_info ""
    log_info "📁 Scripts de deploy antigos:"
    [[ -f "deploy.sh" ]] && log_warning "  - deploy.sh (seria removido)"
    [[ -f "deploy.ps1" ]] && log_warning "  - deploy.ps1 (seria removido)"
    
    log_info ""
    log_info "🐍 Scripts Python não utilizados:"
    [[ -f "fix_articles_module.py" ]] && log_warning "  - fix_articles_module.py (seria removido)"
    [[ -f "verificar_artigos.py" ]] && log_warning "  - verificar_artigos.py (seria removido)"
    [[ -f "corrigir_modulo_artigos.py" ]] && log_warning "  - corrigir_modulo_artigos.py (seria removido)"
    
    log_info ""
    log_info "🔧 Scripts de instalação específicos:"
    [[ -f "install_ubuntu.sh" ]] && log_warning "  - install_ubuntu.sh (seria removido)"
    [[ -f "test_network.sh" ]] && log_warning "  - test_network.sh (seria removido)"
    [[ -f "clean_env.sh" ]] && log_warning "  - clean_env.sh (seria removido)"
    
    log_info ""
    log_info "📚 Documentação duplicada/obsoleta:"
    [[ -f "README_UBUNTU.md" ]] && log_warning "  - README_UBUNTU.md (seria removido)"
    [[ -f "MELHORIAS_UBUNTU.md" ]] && log_warning "  - MELHORIAS_UBUNTU.md (seria removido)"
    [[ -f "RESUMO_MELHORIAS.md" ]] && log_warning "  - RESUMO_MELHORIAS.md (seria removido)"
    [[ -f "DEPLOY_GUIDE.md" ]] && log_warning "  - DEPLOY_GUIDE.md (seria removido)"
    [[ -f "DETECCAO_IP.md" ]] && log_warning "  - DETECCAO_IP.md (seria removido)"
    
    log_info ""
    log_info "🐳 Arquivos Docker não utilizados:"
    [[ -f "docker-compose.min.yml" ]] && log_warning "  - docker-compose.min.yml (seria removido)"
    
    log_info ""
    log_info "📄 Arquivos temporários:"
    [[ -f ".temp_db_config.json" ]] && log_warning "  - .temp_db_config.json (seria removido)"
    
    log_info ""
    log_info "💡 Para executar a limpeza real, use: $0 --execute"
}

# Parse de argumentos
case "${1:-}" in
    --dry-run|--dryrun)
        dry_run
        ;;
    --execute|--force)
        main
        ;;
    --help|-h)
        cat << EOF
Script de Limpeza Profunda - FireFlies

Uso: $0 [OPÇÕES]

OPÇÕES:
    --dry-run, --dryrun    Modo simulação (apenas lista arquivos)
    --execute, --force     Executar limpeza real
    --help, -h             Mostrar esta ajuda

EXEMPLOS:
    $0 --dry-run           # Ver o que seria removido
    $0 --execute           # Executar limpeza real

ARQUIVOS QUE SERÃO REMOVIDOS:
    • Scripts de deploy antigos (deploy.sh, deploy.ps1)
    • Scripts Python não utilizados
    • Scripts de instalação específicos
    • Documentação duplicada/obsoleta
    • Arquivos Docker não utilizados
    • Módulos não utilizados
    • Diretórios de testes vazios
    • Templates não utilizados
    • Arquivos temporários

NOTA: Todos os arquivos removidos serão salvos em backups/cleanup/
EOF
        ;;
    *)
        log_error "Uso: $0 --dry-run ou $0 --execute"
        log_info "Use $0 --help para mais informações"
        exit 1
        ;;
esac 