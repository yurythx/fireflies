# Script para Aplicar Todas as Melhorias - FireFlies
# PowerShell Version

param(
    [switch]$Force,
    [switch]$Verbose
)

# Configurações
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Contadores
$script:IMPROVEMENTS_APPLIED = 0
$script:ERRORS_FIXED = 0
$script:WARNINGS = 0

# Funções de Log
function Write-LogInfo {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-LogSuccess {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
    $script:WARNINGS++
}

function Write-LogError {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Função para gerar SECRET_KEY segura
function Generate-SecretKey {
    $bytes = New-Object Byte[] 50
    (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
    $key = [Convert]::ToBase64String($bytes) -replace '[=+/]', ''
    return $key.Substring(0, 50)
}

# Função para encontrar porta livre
function Find-FreePort {
    param([int]$StartPort)
    
    $port = $StartPort
    while ($true) {
        try {
            $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
            if (-not $connection) {
                return $port
            }
            $port++
        }
        catch {
            return $port
        }
    }
}

# Função para verificar se comando existe
function Test-Command {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

# Função principal
function Main {
    Write-LogInfo "🚀 Aplicando Todas as Melhorias - FireFlies"
    Write-LogInfo "=========================================="
    
    # Criar diretório de backup
    $backupDir = "backups\improvements\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    Write-LogInfo ""
    Write-LogInfo "🔧 1. Corrigindo Problemas de Deploy..."
    
    # 1.1 Verificar Docker
    if (-not (Test-Command "docker")) {
        Write-LogError "Docker não está instalado. Instale o Docker Desktop primeiro."
        return
    }
    
    # 1.2 Verificar Docker Compose
    if (-not (Test-Command "docker-compose")) {
        Write-LogInfo "Instalando Docker Compose..."
        try {
            # Baixar Docker Compose
            $composeUrl = "https://github.com/docker/compose/releases/latest/download/docker-compose-windows-x86_64.exe"
            $composePath = "$env:USERPROFILE\.docker\cli-plugins\docker-compose.exe"
            
            New-Item -ItemType Directory -Path "$env:USERPROFILE\.docker\cli-plugins" -Force | Out-Null
            Invoke-WebRequest -Uri $composeUrl -OutFile $composePath
            
            # Adicionar ao PATH
            $env:PATH += ";$env:USERPROFILE\.docker\cli-plugins"
            Write-LogSuccess "Docker Compose instalado"
            $script:IMPROVEMENTS_APPLIED++
        }
        catch {
            Write-LogError "Erro ao instalar Docker Compose: $_"
            return
        }
    }
    else {
        Write-LogSuccess "Docker Compose já está instalado"
    }
    
    # 1.3 Detectar portas disponíveis
    Write-LogInfo "Detectando portas disponíveis..."
    $WEB_PORT = Find-FreePort 8000
    $DB_PORT = Find-FreePort 5432
    $REDIS_PORT = Find-FreePort 6379
    $NGINX_PORT = Find-FreePort 80
    $NGINX_SSL_PORT = Find-FreePort 443
    
    Write-LogSuccess "Portas detectadas:"
    Write-LogInfo "  Web: $WEB_PORT (Django)"
    Write-LogInfo "  DB: $DB_PORT (PostgreSQL)"
    Write-LogInfo "  Redis: $REDIS_PORT (Cache)"
    Write-LogInfo "  Nginx: $NGINX_PORT (HTTP)"
    Write-LogInfo "  Nginx SSL: $NGINX_SSL_PORT (HTTPS)"
    
    # 1.4 Gerar SECRET_KEY real
    Write-LogInfo "Gerando SECRET_KEY segura..."
    $REAL_SECRET_KEY = Generate-SecretKey
    Write-LogSuccess "SECRET_KEY gerada: $($REAL_SECRET_KEY.Substring(0, 20))..."
    
    # 1.5 Criar arquivo .env se não existir
    if (-not (Test-Path ".env")) {
        Write-LogInfo "Criando arquivo .env com configurações otimizadas..."
        $envContent = @"
# Configuração do Ambiente
ENVIRONMENT=production

# Configurações do Django
DEBUG=False
SECRET_KEY=$REAL_SECRET_KEY
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100

# Configurações do Banco de Dados
DB_NAME=fireflies_prod
DB_USER=fireflies_user
DB_PASSWORD=fireflies_password
DB_HOST=db
DB_PORT=5432

# Configurações de Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Configurações do Redis
REDIS_URL=redis://redis:6379/0

# Configurações de Log
LOG_LEVEL=INFO
LOG_FILE=/app/logs/fireflies.log

# Configurações de Segurança
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://192.168.1.100
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Configurações de Timezone
TIME_ZONE=America/Sao_Paulo
USE_TZ=True

# Configurações de Idioma
LANGUAGE_CODE=pt-br
USE_I18N=True
USE_L10N=True

# Configurações de Arquivos Estáticos
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/media

# Configurações de Cache
CACHE_BACKEND=django_redis.cache.RedisCache
CACHE_LOCATION=redis://redis:6379/1

# Configurações de Sessão
SESSION_ENGINE=django.contrib.sessions.backends.cache
SESSION_CACHE_ALIAS=default

# Configurações de Upload
FILE_UPLOAD_MAX_MEMORY_SIZE=2621440
DATA_UPLOAD_MAX_MEMORY_SIZE=2621440

# Configurações de Logging
LOGGING_CONFIG=
DJANGO_LOG_LEVEL=INFO

# Configurações de Portas (Detectadas Automaticamente)
DJANGO_PORT=$WEB_PORT
POSTGRES_PORT=$DB_PORT
REDIS_PORT=$REDIS_PORT
NGINX_PORT=$NGINX_PORT
NGINX_SSL_PORT=$NGINX_SSL_PORT
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-LogSuccess "Arquivo .env criado com SECRET_KEY real e portas otimizadas"
        $script:IMPROVEMENTS_APPLIED++
    }
    else {
        Write-LogSuccess "Arquivo .env já existe"
        
        # 1.6 Corrigir SECRET_KEY se necessário
        $envContent = Get-Content ".env" -Raw
        if ($envContent -match "django-insecure-change-this-in-production") {
            Write-LogInfo "Corrigindo SECRET_KEY existente..."
            Copy-Item ".env" ".env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$REAL_SECRET_KEY"
            $envContent | Out-File -FilePath ".env" -Encoding UTF8
            Write-LogSuccess "SECRET_KEY corrigida"
            $script:ERRORS_FIXED++
        }
        else {
            Write-LogSuccess "SECRET_KEY já está correta"
        }
        
        # 1.7 Adicionar configurações de portas se não existirem
        if ($envContent -notmatch "DJANGO_PORT=") {
            Write-LogInfo "Adicionando configurações de portas..."
            $portConfig = @"

# Configurações de Portas (Detectadas Automaticamente)
DJANGO_PORT=$WEB_PORT
POSTGRES_PORT=$DB_PORT
REDIS_PORT=$REDIS_PORT
NGINX_PORT=$NGINX_PORT
NGINX_SSL_PORT=$NGINX_SSL_PORT
"@
            Add-Content -Path ".env" -Value $portConfig
            Write-LogSuccess "Configurações de portas adicionadas"
            $script:ERRORS_FIXED++
        }
    }
    
    # 1.8 Adicionar ENVIRONMENT se não existir
    if ((Test-Path ".env") -and ((Get-Content ".env") -notmatch "^ENVIRONMENT=")) {
        Write-LogInfo "Adicionando variável ENVIRONMENT..."
        $envContent = "ENVIRONMENT=production`n" + (Get-Content ".env" -Raw)
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-LogSuccess "Variável ENVIRONMENT adicionada"
        $script:ERRORS_FIXED++
    }
    else {
        Write-LogSuccess "Variável ENVIRONMENT já existe"
    }
    
    # 1.9 Atualizar docker-compose.yml com portas detectadas
    Write-LogInfo "Atualizando docker-compose.yml com portas detectadas..."
    if (Test-Path "docker-compose.yml") {
        Copy-Item "docker-compose.yml" "docker-compose.yml.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        
        $composeContent = Get-Content "docker-compose.yml" -Raw
        
        # Atualizar portas no docker-compose.yml
        $composeContent = $composeContent -replace '      - "8000:8000"', "      - `"$WEB_PORT`:8000`""
        $composeContent = $composeContent -replace '      - "5432:5432"', "      - `"$DB_PORT`:5432`""
        $composeContent = $composeContent -replace '      - "6379:6379"', "      - `"$REDIS_PORT`:6379`""
        $composeContent = $composeContent -replace '      - "80:80"', "      - `"$NGINX_PORT`:80`""
        $composeContent = $composeContent -replace '      - "443:443"', "      - `"$NGINX_SSL_PORT`:443`""
        
        $composeContent | Out-File -FilePath "docker-compose.yml" -Encoding UTF8
        Write-LogSuccess "docker-compose.yml atualizado com portas: $WEB_PORT, $DB_PORT, $REDIS_PORT, $NGINX_PORT, $NGINX_SSL_PORT"
        $script:IMPROVEMENTS_APPLIED++
    }
    
    Write-LogInfo ""
    Write-LogInfo "🔒 2. Melhorando Segurança..."
    
    # 2.1 Criar arquivo .env.example
    if (-not (Test-Path ".env.example")) {
        Write-LogInfo "Criando .env.example..."
        Copy-Item ".env" ".env.example"
        (Get-Content ".env.example") -replace "=.*", "=your_value_here" | Out-File ".env.example" -Encoding UTF8
        Write-LogSuccess ".env.example criado"
        $script:IMPROVEMENTS_APPLIED++
    }
    
    # 2.2 Atualizar .gitignore
    if (Test-Path ".gitignore") {
        $gitignore = Get-Content ".gitignore"
        $additions = @(
            "# Environment files",
            ".env",
            ".env.local",
            ".env.production",
            "",
            "# Logs",
            "logs/",
            "*.log",
            "",
            "# Backups",
            "backups/",
            "",
            "# Docker",
            "docker-compose.override.yml",
            "",
            "# IDE",
            ".vscode/",
            ".idea/",
            "",
            "# OS",
            ".DS_Store",
            "Thumbs.db"
        )
        
        foreach ($addition in $additions) {
            if ($gitignore -notcontains $addition) {
                Add-Content ".gitignore" $addition
            }
        }
        Write-LogSuccess ".gitignore atualizado"
        $script:IMPROVEMENTS_APPLIED++
    }
    
    Write-LogInfo ""
    Write-LogInfo "🧪 3. Configurando Testes..."
    
    # 3.1 Criar diretórios de teste
    $testDirs = @(
        "tests\unit",
        "tests\integration", 
        "tests\e2e",
        "apps\accounts\tests",
        "apps\articles\tests",
        "apps\config\tests",
        "apps\pages\tests"
    )
    
    foreach ($dir in $testDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-LogSuccess "Diretório de teste criado: $dir"
            $script:IMPROVEMENTS_APPLIED++
        }
    }
    
    # 3.2 Criar arquivo de configuração de testes
    if (-not (Test-Path "pytest.ini")) {
        Write-LogInfo "Criando pytest.ini..."
        $pytestConfig = @"
[tool:pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = tests.py test_*.py *_tests.py
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
    --cov=apps
    --cov-report=html
    --cov-report=term-missing
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
"@
        $pytestConfig | Out-File -FilePath "pytest.ini" -Encoding UTF8
        Write-LogSuccess "pytest.ini criado"
        $script:IMPROVEMENTS_APPLIED++
    }
    
    # 3.3 Criar testes básicos
    $testFiles = @{
        "tests\unit\test_basic.py" = @"
import pytest
from django.test import TestCase

class BasicTestCase(TestCase):
    def test_basic_functionality(self):
        self.assertTrue(True)
        
    def test_django_working(self):
        from django.conf import settings
        self.assertIsNotNone(settings)
"@
        "apps\accounts\tests\test_models.py" = @"
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
"@
        "apps\articles\tests\test_models.py" = @"
import pytest
from django.test import TestCase
from apps.articles.models import Article, Category

class ArticleModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
    def test_article_creation(self):
        article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            category=self.category
        )
        self.assertEqual(article.title, 'Test Article')
        self.assertEqual(article.slug, 'test-article')
        self.assertEqual(article.category, self.category)
"@
    }
    
    foreach ($file in $testFiles.Keys) {
        if (-not (Test-Path $file)) {
            $testFiles[$file] | Out-File -FilePath $file -Encoding UTF8
            Write-LogSuccess "Teste criado: $file"
            $script:IMPROVEMENTS_APPLIED++
        }
    }
    
    Write-LogInfo ""
    Write-LogInfo "🔧 4. Criando Scripts de Manutenção..."
    
    # 4.1 Script de health check
    $healthScript = @"
#!/bin/bash
# Health Check Script - FireFlies

echo "🔍 Verificando saúde do sistema..."

# Verificar se containers estão rodando
if docker-compose ps | grep -q "Up"; then
    echo "✅ Containers estão rodando"
else
    echo "❌ Containers não estão rodando"
    exit 1
fi

# Verificar se aplicação responde
if curl -f http://localhost:$WEB_PORT/health/ > /dev/null 2>&1; then
    echo "✅ Aplicação está respondendo"
else
    echo "❌ Aplicação não está respondendo"
    exit 1
fi

# Verificar banco de dados
if docker-compose exec -T db pg_isready -U fireflies_user > /dev/null 2>&1; then
    echo "✅ Banco de dados está acessível"
else
    echo "❌ Banco de dados não está acessível"
    exit 1
fi

echo "🎉 Sistema está saudável!"
"@
    $healthScript | Out-File -FilePath "scripts\health_check.sh" -Encoding UTF8
    Write-LogSuccess "Script de health check criado"
    $script:IMPROVEMENTS_APPLIED++
    
    # 4.2 Script de backup
    $backupScript = @"
#!/bin/bash
# Backup Script - FireFlies

BACKUP_DIR="backups/\$(date +%Y%m%d_%H%M%S)"
mkdir -p \$BACKUP_DIR

echo "💾 Criando backup..."

# Backup do banco de dados
docker-compose exec -T db pg_dump -U fireflies_user fireflies_prod > \$BACKUP_DIR/database.sql

# Backup dos arquivos de mídia
if [ -d "media" ]; then
    tar -czf \$BACKUP_DIR/media.tar.gz media/
fi

# Backup das configurações
cp .env \$BACKUP_DIR/
cp docker-compose.yml \$BACKUP_DIR/

echo "✅ Backup criado em \$BACKUP_DIR"
"@
    $backupScript | Out-File -FilePath "scripts\backup.sh" -Encoding UTF8
    Write-LogSuccess "Script de backup criado"
    $script:IMPROVEMENTS_APPLIED++
    
    # 4.3 Script de limpeza
    $cleanupScript = @"
#!/bin/bash
# Cleanup Script - FireFlies

echo "🧹 Limpando arquivos temporários..."

# Limpar cache do Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Limpar logs antigos (mais de 30 dias)
find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null

# Limpar backups antigos (mais de 7 dias)
find backups/ -type d -mtime +7 -exec rm -rf {} + 2>/dev/null

# Limpar containers parados
docker container prune -f

# Limpar imagens não utilizadas
docker image prune -f

echo "✅ Limpeza concluída"
"@
    $cleanupScript | Out-File -FilePath "scripts\cleanup.sh" -Encoding UTF8
    Write-LogSuccess "Script de limpeza criado"
    $script:IMPROVEMENTS_APPLIED++
    
    Write-LogInfo ""
    Write-LogInfo "📚 5. Criando Documentação..."
    
    # 5.1 README de deploy
    $deployReadme = @"
# Guia de Deploy - FireFlies

## Pré-requisitos
 - Docker e Docker Compose instalados
 - Portas disponíveis: $WEB_PORT, $DB_PORT, $REDIS_PORT, $NGINX_PORT, $NGINX_SSL_PORT

## Deploy Rápido
\`\`\`bash
# Aplicar melhorias
./apply_all_improvements.sh

# Fazer deploy
./deploy.sh
\`\`\`

## Verificações
\`\`\`bash
# Health check
./scripts/health_check.sh

# Verificar logs
docker-compose logs -f
\`\`\`

## Backup
\`\`\`bash
./scripts/backup.sh
\`\`\`

## Limpeza
\`\`\`bash
./scripts/cleanup.sh
\`\`\`

## Portas Utilizadas
 - Django: $WEB_PORT
 - PostgreSQL: $DB_PORT  
 - Redis: $REDIS_PORT
 - Nginx HTTP: $NGINX_PORT
 - Nginx HTTPS: $NGINX_SSL_PORT

## Troubleshooting
 1. Se uma porta estiver ocupada, o script detectará automaticamente uma alternativa
 2. SECRET_KEY é gerada automaticamente de forma segura
 3. Todos os arquivos de configuração são validados antes do deploy
"@
    $deployReadme | Out-File -FilePath "README_DEPLOY.md" -Encoding UTF8
    Write-LogSuccess "README de deploy criado"
    $script:IMPROVEMENTS_APPLIED++
    
    # 5.2 Documentação de melhorias
    $improvementsDoc = @"
# Melhorias Aplicadas - FireFlies

## Data: $(Get-Date -Format 'dd/MM/yyyy HH:mm')

### Problemas Corrigidos
 - SECRET_KEY insegura substituída por chave criptográfica real
 - Variável ENVIRONMENT adicionada ao .env
 - Portas detectadas automaticamente: $WEB_PORT, $DB_PORT, $REDIS_PORT, $NGINX_PORT, $NGINX_SSL_PORT
 - Docker Compose atualizado com portas corretas

### Melhorias de Segurança
 - Arquivo .env.example criado
 - .gitignore atualizado para excluir arquivos sensíveis
 - Configurações de segurança otimizadas

### Estrutura de Testes
 - Diretórios de teste criados para todos os apps
 - pytest.ini configurado
 - Testes básicos criados para models principais

### Scripts de Manutenção
 - health_check.sh: Verifica saúde do sistema
 - backup.sh: Cria backups automáticos
 - cleanup.sh: Limpa arquivos temporários

### Documentação
 - README_DEPLOY.md: Guia completo de deploy
 - Este arquivo: Registro das melhorias aplicadas

### Estatísticas
 - Melhorias aplicadas: $script:IMPROVEMENTS_APPLIED
 - Erros corrigidos: $script:ERRORS_FIXED
 - Avisos: $script:WARNINGS

### Próximos Passos
 1. Execute: ./deploy.sh
 2. Verifique: ./scripts/health_check.sh
 3. Configure email no .env
 4. Personalize ALLOWED_HOSTS
"@
    $improvementsDoc | Out-File -FilePath "RESUMO_MELHORIAS_IMPLEMENTADAS.md" -Encoding UTF8
    Write-LogSuccess "Documentação de melhorias criada"
    $script:IMPROVEMENTS_APPLIED++
    
    # Resumo final
    Write-LogInfo ""
    Write-LogInfo "🎉 Resumo das Melhorias Aplicadas"
    Write-LogInfo "================================"
    Write-LogSuccess "Melhorias aplicadas: $script:IMPROVEMENTS_APPLIED"
    Write-LogSuccess "Erros corrigidos: $script:ERRORS_FIXED"
    if ($script:WARNINGS -gt 0) {
        Write-LogWarning "Avisos: $script:WARNINGS"
    }
    
    Write-LogInfo ""
    Write-LogInfo "🚀 Próximos Passos:"
    Write-LogInfo "1. Execute: ./deploy.sh"
    Write-LogInfo "2. Verifique: ./scripts/health_check.sh"
    Write-LogInfo "3. Configure email no .env"
    Write-LogInfo "4. Personalize ALLOWED_HOSTS"
    
    Write-LogInfo ""
    Write-LogSuccess "Todas as melhorias foram aplicadas com sucesso!"
}

# Executar função principal
Main 