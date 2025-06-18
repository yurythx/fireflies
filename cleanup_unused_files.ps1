# Script de Limpeza Profunda - FireFlies (PowerShell)
# Remove arquivos não utilizados do projeto

param(
    [switch]$DryRun,
    [switch]$Execute,
    [switch]$Help
)

# Cores para output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Contadores
$FilesRemoved = 0
$FilesKept = 0
$TotalSizeRemoved = 0

# Função de log
function Write-Log {
    param(
        [string]$Message,
        [string]$Color = $White
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info {
    param([string]$Message)
    Write-Log "[INFO] $Message" $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Log "[SUCCESS] $Message" $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Log "[WARNING] $Message" $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Log "[ERROR] $Message" $Red
}

# Função para calcular tamanho de arquivo
function Get-FileSize {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        $file = Get-Item $FilePath
        return $file.Length
    }
    return 0
}

# Função para remover arquivo com backup
function Remove-FileWithBackup {
    param(
        [string]$FilePath,
        [string]$Reason
    )
    
    if (Test-Path $FilePath) {
        $size = Get-FileSize $FilePath
        
        # Criar backup
        $backupDir = "backups\cleanup\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        
        # Mover para backup
        Move-Item $FilePath $backupDir\
        
        Write-Success "Removido: $FilePath ($Reason) - Backup em: $backupDir\"
        $script:FilesRemoved++
        $script:TotalSizeRemoved += $size
    }
}

# Função para remover diretório com backup
function Remove-DirectoryWithBackup {
    param(
        [string]$DirPath,
        [string]$Reason
    )
    
    if (Test-Path $DirPath) {
        # Criar backup
        $backupDir = "backups\cleanup\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        
        # Mover para backup
        Move-Item $DirPath $backupDir\
        
        Write-Success "Removido: $DirPath ($Reason) - Backup em: $backupDir\"
        $script:FilesRemoved++
    }
}

# Função para verificar se arquivo é usado
function Test-FileUsage {
    param(
        [string]$FilePath,
        [string]$SearchPattern
    )
    
    $excludeDirs = @(".git", "backups", "node_modules", "__pycache__")
    $excludeFiles = @("*.pyc", "*.log")
    
    $searchResult = Get-ChildItem -Recurse -Exclude $excludeDirs | 
                   Where-Object { $_.Name -notlike $excludeFiles } |
                   Select-String -Pattern $SearchPattern -Quiet
    
    return $searchResult
}

# Função principal de limpeza
function Start-Cleanup {
    Write-Info "Iniciando limpeza profunda do projeto FireFlies"
    Write-Info "=================================================="
    
    # Criar diretório de backup
    $backupDir = "backups\cleanup\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    Write-Info ""
    Write-Info "1. Removendo scripts de deploy antigos..."
    
    # Scripts de deploy antigos (substituídos pelo deploy_improved.sh)
    if (Test-Path "deploy.sh") {
        Remove-FileWithBackup "deploy.sh" "Substituído por deploy_improved.sh"
    }
    
    if (Test-Path "deploy.ps1") {
        Remove-FileWithBackup "deploy.ps1" "Substituído por deploy_improved.sh"
    }
    
    Write-Info ""
    Write-Info "2. Removendo scripts Python não utilizados..."
    
    # Scripts Python não utilizados
    if (Test-Path "fix_articles_module.py") {
        Remove-FileWithBackup "fix_articles_module.py" "Script não utilizado"
    }
    
    if (Test-Path "verificar_artigos.py") {
        Remove-FileWithBackup "verificar_artigos.py" "Script não utilizado"
    }
    
    if (Test-Path "corrigir_modulo_artigos.py") {
        Remove-FileWithBackup "corrigir_modulo_artigos.py" "Script não utilizado"
    }
    
    Write-Info ""
    Write-Info "3. Removendo scripts de instalação específicos..."
    
    # Scripts de instalação específicos (já executados)
    if (Test-Path "install_ubuntu.sh") {
        Remove-FileWithBackup "install_ubuntu.sh" "Script de instalação já executado"
    }
    
    if (Test-Path "test_network.sh") {
        Remove-FileWithBackup "test_network.sh" "Script de teste de rede não utilizado"
    }
    
    if (Test-Path "clean_env.sh") {
        Remove-FileWithBackup "clean_env.sh" "Script de limpeza de ambiente não utilizado"
    }
    
    Write-Info ""
    Write-Info "4. Removendo documentação duplicada/obsoleta..."
    
    # Documentação duplicada/obsoleta
    if (Test-Path "README_UBUNTU.md") {
        Remove-FileWithBackup "README_UBUNTU.md" "Documentação específica Ubuntu obsoleta"
    }
    
    if (Test-Path "MELHORIAS_UBUNTU.md") {
        Remove-FileWithBackup "MELHORIAS_UBUNTU.md" "Documentação de melhorias Ubuntu obsoleta"
    }
    
    if (Test-Path "RESUMO_MELHORIAS.md") {
        Remove-FileWithBackup "RESUMO_MELHORIAS.md" "Substituído por RESUMO_MELHORIAS_IMPLEMENTADAS.md"
    }
    
    if (Test-Path "DEPLOY_GUIDE.md") {
        Remove-FileWithBackup "DEPLOY_GUIDE.md" "Guia de deploy obsoleto"
    }
    
    if (Test-Path "DETECCAO_IP.md") {
        Remove-FileWithBackup "DETECCAO_IP.md" "Documentação de detecção de IP obsoleta"
    }
    
    Write-Info ""
    Write-Info "5. Removendo arquivos Docker não utilizados..."
    
    # Arquivos Docker não utilizados
    if (Test-Path "docker-compose.min.yml") {
        Remove-FileWithBackup "docker-compose.min.yml" "Arquivo docker-compose mínimo não utilizado"
    }
    
    Write-Info ""
    Write-Info "6. Removendo módulos não utilizados..."
    
    # Módulo common não utilizado
    if (Test-Path "apps\common") {
        if (-not (Test-FileUsage "apps\common" "from apps.common")) {
            Remove-DirectoryWithBackup "apps\common" "Módulo common não utilizado"
        } else {
            Write-Warning "Mantido: apps\common (pode estar sendo usado)"
            $script:FilesKept++
        }
    }
    
    # Módulo core não utilizado
    if (Test-Path "apps\core") {
        if (-not (Test-FileUsage "apps\core" "from apps.core")) {
            Remove-DirectoryWithBackup "apps\core" "Módulo core não utilizado"
        } else {
            Write-Warning "Mantido: apps\core (pode estar sendo usado)"
            $script:FilesKept++
        }
    }
    
    Write-Info ""
    Write-Info "7. Removendo diretórios de testes vazios..."
    
    # Diretórios de testes vazios
    if (Test-Path "tests") {
        $testFiles = Get-ChildItem "tests" -Filter "*.py" -Recurse
        if ($testFiles.Count -eq 1) {
            Remove-DirectoryWithBackup "tests" "Diretório de testes vazio"
        }
    }
    
    # Verificar diretórios de testes vazios nos apps
    Get-ChildItem "apps" -Directory | ForEach-Object {
        $testDir = Join-Path $_.FullName "tests"
        if (Test-Path $testDir) {
            $testFiles = Get-ChildItem $testDir -Filter "*.py" -Recurse
            if ($testFiles.Count -eq 1) {
                Remove-DirectoryWithBackup $testDir "Diretório de testes vazio"
            }
        }
    }
    
    Write-Info ""
    Write-Info "8. Removendo templates não utilizados..."
    
    # Templates não utilizados
    if (Test-Path "templates\admin\base_site.html") {
        if (-not (Test-FileUsage "templates\admin\base_site.html" "base_site.html")) {
            Remove-FileWithBackup "templates\admin\base_site.html" "Template admin não utilizado"
        } else {
            Write-Warning "Mantido: templates\admin\base_site.html (pode estar sendo usado)"
            $script:FilesKept++
        }
    }
    
    Write-Info ""
    Write-Info "9. Removendo arquivos temporários..."
    
    # Arquivos temporários
    if (Test-Path ".temp_db_config.json") {
        Remove-FileWithBackup ".temp_db_config.json" "Arquivo temporário de configuração"
    }
    
    # Manter .first_install pois é usado pelo sistema
    if (Test-Path ".first_install") {
        Write-Info "Mantido: .first_install (usado pelo sistema de deploy)"
        $script:FilesKept++
    }
    
    Write-Info ""
    Write-Info "10. Limpando arquivos de configuração duplicados..."
    
    # Verificar se há arquivos de configuração duplicados
    if ((Test-Path "pytest.ini") -and (Test-Path ".coveragerc")) {
        # Manter ambos pois são para propósitos diferentes
        Write-Info "Mantidos: pytest.ini e .coveragerc (configurações de teste)"
        $script:FilesKept += 2
    }
    
    Write-Info ""
    Write-Info "11. Verificando arquivos estáticos..."
    
    # Verificar se staticfiles está sendo usado
    if (Test-Path "staticfiles") {
        Write-Info "Mantido: staticfiles\ (gerado pelo Django collectstatic)"
        $script:FilesKept++
    }
    
    Write-Info ""
    Write-Info "RESUMO DA LIMPEZA"
    Write-Info "===================="
    Write-Info "Arquivos removidos: $FilesRemoved"
    Write-Info "Arquivos mantidos: $FilesKept"
    
    if ($TotalSizeRemoved -gt 0) {
        $sizeMB = [math]::Round($TotalSizeRemoved / 1MB, 2)
        Write-Info "Espaço liberado: ${sizeMB}MB"
    }
    
    Write-Info ""
    Write-Info "Backups salvos em: backups\cleanup\"
    Write-Info ""
    Write-Info "Limpeza concluída!"
    
    # Sugestões adicionais
    Write-Info ""
    Write-Info "Sugestões adicionais:"
    Write-Info "  • Execute: git status para ver mudanças"
    Write-Info "  • Execute: git add . para adicionar mudanças"
    Write-Info "  • Execute: git commit -m 'Cleanup: remove unused files'"
    Write-Info "  • Verifique: backups\cleanup\ antes de fazer commit"
}

# Função de limpeza segura (apenas lista arquivos)
function Start-DryRun {
    Write-Info "Modo DRY RUN - Apenas listando arquivos que seriam removidos"
    Write-Info "================================================================"
    
    Write-Info ""
    Write-Info "Scripts de deploy antigos:"
    if (Test-Path "deploy.sh") { Write-Warning "  - deploy.sh (seria removido)" }
    if (Test-Path "deploy.ps1") { Write-Warning "  - deploy.ps1 (seria removido)" }
    
    Write-Info ""
    Write-Info "Scripts Python não utilizados:"
    if (Test-Path "fix_articles_module.py") { Write-Warning "  - fix_articles_module.py (seria removido)" }
    if (Test-Path "verificar_artigos.py") { Write-Warning "  - verificar_artigos.py (seria removido)" }
    if (Test-Path "corrigir_modulo_artigos.py") { Write-Warning "  - corrigir_modulo_artigos.py (seria removido)" }
    
    Write-Info ""
    Write-Info "Scripts de instalação específicos:"
    if (Test-Path "install_ubuntu.sh") { Write-Warning "  - install_ubuntu.sh (seria removido)" }
    if (Test-Path "test_network.sh") { Write-Warning "  - test_network.sh (seria removido)" }
    if (Test-Path "clean_env.sh") { Write-Warning "  - clean_env.sh (seria removido)" }
    
    Write-Info ""
    Write-Info "Documentação duplicada/obsoleta:"
    if (Test-Path "README_UBUNTU.md") { Write-Warning "  - README_UBUNTU.md (seria removido)" }
    if (Test-Path "MELHORIAS_UBUNTU.md") { Write-Warning "  - MELHORIAS_UBUNTU.md (seria removido)" }
    if (Test-Path "RESUMO_MELHORIAS.md") { Write-Warning "  - RESUMO_MELHORIAS.md (seria removido)" }
    if (Test-Path "DEPLOY_GUIDE.md") { Write-Warning "  - DEPLOY_GUIDE.md (seria removido)" }
    if (Test-Path "DETECCAO_IP.md") { Write-Warning "  - DETECCAO_IP.md (seria removido)" }
    
    Write-Info ""
    Write-Info "Arquivos Docker não utilizados:"
    if (Test-Path "docker-compose.min.yml") { Write-Warning "  - docker-compose.min.yml (seria removido)" }
    
    Write-Info ""
    Write-Info "Arquivos temporários:"
    if (Test-Path ".temp_db_config.json") { Write-Warning "  - .temp_db_config.json (seria removido)" }
    
    Write-Info ""
    Write-Info "Para executar a limpeza real, use: .\cleanup_unused_files.ps1 -Execute"
}

# Função de ajuda
function Show-Help {
    Write-Info "Script de Limpeza Profunda - FireFlies (PowerShell)"
    Write-Info ""
    Write-Info "Uso: .\cleanup_unused_files.ps1 [OPÇÕES]"
    Write-Info ""
    Write-Info "OPÇÕES:"
    Write-Info "    -DryRun              Modo simulação (apenas lista arquivos)"
    Write-Info "    -Execute             Executar limpeza real"
    Write-Info "    -Help                Mostrar esta ajuda"
    Write-Info ""
    Write-Info "EXEMPLOS:"
    Write-Info "    .\cleanup_unused_files.ps1 -DryRun           # Ver o que seria removido"
    Write-Info "    .\cleanup_unused_files.ps1 -Execute          # Executar limpeza real"
    Write-Info ""
    Write-Info "ARQUIVOS QUE SERÃO REMOVIDOS:"
    Write-Info "    • Scripts de deploy antigos (deploy.sh, deploy.ps1)"
    Write-Info "    • Scripts Python não utilizados"
    Write-Info "    • Scripts de instalação específicos"
    Write-Info "    • Documentação duplicada/obsoleta"
    Write-Info "    • Arquivos Docker não utilizados"
    Write-Info "    • Módulos não utilizados"
    Write-Info "    • Diretórios de testes vazios"
    Write-Info "    • Templates não utilizados"
    Write-Info "    • Arquivos temporários"
    Write-Info ""
    Write-Info "NOTA: Todos os arquivos removidos serão salvos em backups\cleanup\"
}

# Execução principal
if ($Help) {
    Show-Help
} elseif ($DryRun) {
    Start-DryRun
} elseif ($Execute) {
    Start-Cleanup
} else {
    Write-Error "Uso: .\cleanup_unused_files.ps1 -DryRun ou .\cleanup_unused_files.ps1 -Execute"
    Write-Info "Use .\cleanup_unused_files.ps1 -Help para mais informações"
    exit 1
} 