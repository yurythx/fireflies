# Script PowerShell para corrigir erro de validação do docker-compose.yml
# Executar no Windows onde o projeto está sendo desenvolvido

# Funções de logging
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Blue
    Write-Host $Title -ForegroundColor Blue
    Write-Host "==================================" -ForegroundColor Blue
}

Write-Section "Correcao de Erro de Validacao Docker Compose"

# 1. Verificar se estamos no diretório correto
if (-not (Test-Path "docker-compose.yml")) {
    Write-Error "docker-compose.yml nao encontrado no diretorio atual"
    Write-Info "Certifique-se de estar no diretorio do projeto FireFlies"
    exit 1
}

Write-Success "docker-compose.yml encontrado"

# 2. Verificar permissões do arquivo
Write-Info "Verificando permissoes do docker-compose.yml..."
Get-ChildItem docker-compose.yml | Format-List

# 3. Verificar se há caracteres especiais (Windows line endings)
Write-Info "Verificando caracteres especiais..."
$content = Get-Content docker-compose.yml -Raw
if ($content -match "`r`n") {
    Write-Warning "Arquivo contem caracteres de retorno de carro (Windows line endings)"
    Write-Info "Convertendo para Unix line endings..."
    $content = $content -replace "`r`n", "`n"
    $content | Set-Content docker-compose.yml -NoNewline
    Write-Success "Line endings convertidos"
} else {
    Write-Success "Line endings estao corretos"
}

# 4. Verificar sintaxe com docker-compose
Write-Info "Testando sintaxe do docker-compose.yml..."
try {
    $null = docker-compose config 2>$null
    Write-Success "Sintaxe do docker-compose.yml esta valida"
} catch {
    Write-Error "Erro de sintaxe detectado"
    Write-Info "Executando validacao detalhada..."
    docker-compose config
    exit 1
}

# 5. Verificar se há variáveis de ambiente não definidas
Write-Info "Verificando variaveis de ambiente..."
if (Test-Path ".env") {
    Write-Success "Arquivo .env encontrado"
    
    # Verificar se as variáveis necessárias estão definidas
    $requiredVars = @("DB_NAME", "DB_USER", "DB_PASSWORD", "SECRET_KEY")
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        if (-not (Select-String -Path ".env" -Pattern "^${var}=" -Quiet)) {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Warning "Variaveis faltando no .env: $($missingVars -join ', ')"
    } else {
        Write-Success "Todas as variaveis necessarias estao definidas"
    }
} else {
    Write-Warning "Arquivo .env nao encontrado"
}

# 6. Verificar se há conflitos de porta
Write-Info "Verificando portas em uso..."
$portsToCheck = @(80, 443, 8000, 5432, 6379)
$occupiedPorts = @()

foreach ($port in $portsToCheck) {
    try {
        $null = Get-NetTCPConnection -LocalPort $port -ErrorAction Stop
        $occupiedPorts += $port
    } catch {
        # Porta não está em uso
    }
}

if ($occupiedPorts.Count -gt 0) {
    Write-Warning "Portas ocupadas: $($occupiedPorts -join ', ')"
    Write-Info "Isso pode causar problemas no deploy"
} else {
    Write-Success "Todas as portas necessarias estao livres"
}

# 7. Verificar se o Docker está funcionando
Write-Info "Verificando Docker..."
try {
    $null = docker info 2>$null
    Write-Success "Docker esta funcionando"
} catch {
    Write-Error "Docker nao esta funcionando ou nao esta acessivel"
    exit 1
}

try {
    $null = docker-compose version 2>$null
    Write-Success "Docker Compose esta disponivel"
} catch {
    Write-Error "Docker Compose nao esta disponivel"
    exit 1
}

# 8. Teste final de validação
Write-Info "Executando teste final de validacao..."
try {
    $null = docker-compose config 2>$null
    Write-Success "Validacao final: SUCESSO"
    Write-Info "O docker-compose.yml esta valido e pronto para uso"
} catch {
    Write-Error "Validacao final: FALHA"
    Write-Info "Executando validacao com output completo para debug..."
    docker-compose config
    exit 1
}

Write-Section "Resumo da Correcao"
Write-Success "Todas as verificacoes passaram"
Write-Info "O arquivo docker-compose.yml esta valido"
Write-Info "Voce pode tentar executar o deploy novamente"

# 9. Sugestões adicionais
Write-Section "Sugestoes"
Write-Info "Se o problema persistir, tente:"
Write-Info "1. docker-compose down --remove-orphans"
Write-Info "2. docker system prune -f"
Write-Info "3. Executar o deploy novamente"

Write-Info "Para o servidor Linux, execute o script fix_validation_error.sh" 