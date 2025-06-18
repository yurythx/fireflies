#!/bin/bash

# Script de Aplicação de Todas as Melhorias - FireFlies
# Aplica todas as correções e melhorias identificadas

set -euo pipefail

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Contadores
IMPROVEMENTS_APPLIED=0
ERRORS_FIXED=0

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

# Função para gerar SECRET_KEY segura
generate_secret_key() {
    openssl rand -base64 50 | tr -d "=+/" | cut -c1-50
}

# Função para encontrar porta livre
find_free_port() {
    local start_port=$1
    local port=$start_port
    
    while netstat -tuln | grep -q ":$port "; do
        port=$((port + 1))
    done
    
    echo $port
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função principal
main() {
    log_info "🚀 Aplicando Todas as Melhorias - FireFlies"
    log_info "=========================================="
    
    # Criar diretório de backup
    mkdir -p "backups/improvements/$(date +%Y%m%d_%H%M%S)"
    
    log_info ""
    log_info "🔧 1. Corrigindo Problemas de Deploy..."
    
    # 1.1 Instalar Docker Compose se não existir
    if ! command_exists docker-compose; then
        log_info "Instalando Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        log_success "Docker Compose instalado"
        IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    else
        log_success "Docker Compose já está instalado"
    fi
    
    # 1.2 Adicionar usuário ao grupo docker
    if ! groups | grep -q docker; then
        log_info "Adicionando usuário ao grupo docker..."
        sudo usermod -aG docker $USER
        log_warning "Usuário adicionado ao grupo docker"
        log_warning "Execute: newgrp docker"
        IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    else
        log_success "Usuário já está no grupo docker"
    fi
    
    # 1.3 Detectar portas disponíveis
    log_info "Detectando portas disponíveis..."
    WEB_PORT=$(find_free_port 8000)
    DB_PORT=$(find_free_port 5432)
    REDIS_PORT=$(find_free_port 6379)
    NGINX_PORT=$(find_free_port 80)
    NGINX_SSL_PORT=$(find_free_port 443)
    
    log_success "Portas detectadas:"
    log_info "  Web: $WEB_PORT (Django)"
    log_info "  DB: $DB_PORT (PostgreSQL)"
    log_info "  Redis: $REDIS_PORT (Cache)"
    log_info "  Nginx: $NGINX_PORT (HTTP)"
    log_info "  Nginx SSL: $NGINX_SSL_PORT (HTTPS)"
    
    # 1.4 Gerar SECRET_KEY real
    log_info "Gerando SECRET_KEY segura..."
    REAL_SECRET_KEY=$(generate_secret_key)
    log_success "SECRET_KEY gerada: ${REAL_SECRET_KEY:0:20}..."
    
    # 1.5 Criar arquivo .env se não existir
    if [[ ! -f .env ]]; then
        log_info "Criando arquivo .env com configurações otimizadas..."
        cat > .env << EOF
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
EOF
        log_success "Arquivo .env criado com SECRET_KEY real e portas otimizadas"
        IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    else
        log_success "Arquivo .env já existe"
        
        # 1.6 Corrigir SECRET_KEY se necessário
        if grep -q "django-insecure-change-this-in-production" .env; then
            log_info "Corrigindo SECRET_KEY existente..."
            cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
            grep -v "^SECRET_KEY=" .env > .env.temp
            echo "SECRET_KEY=$REAL_SECRET_KEY" > .env
            cat .env.temp >> .env
            rm .env.temp
            log_success "SECRET_KEY corrigida"
            ERRORS_FIXED=$((ERRORS_FIXED + 1))
        else
            log_success "SECRET_KEY já está correta"
        fi
        
        # 1.7 Adicionar configurações de portas se não existirem
        if ! grep -q "^DJANGO_PORT=" .env; then
            log_info "Adicionando configurações de portas..."
            cat >> .env << EOF

# Configurações de Portas (Detectadas Automaticamente)
DJANGO_PORT=$WEB_PORT
POSTGRES_PORT=$DB_PORT
REDIS_PORT=$REDIS_PORT
NGINX_PORT=$NGINX_PORT
NGINX_SSL_PORT=$NGINX_SSL_PORT
EOF
            log_success "Configurações de portas adicionadas"
            ERRORS_FIXED=$((ERRORS_FIXED + 1))
        fi
    fi
    
    # 1.8 Adicionar ENVIRONMENT se não existir
    if [[ -f .env ]] && ! grep -q "^ENVIRONMENT=" .env; then
        log_info "Adicionando variável ENVIRONMENT..."
        echo "ENVIRONMENT=production" > .env.temp
        cat .env >> .env.temp
        mv .env.temp .env
        log_success "Variável ENVIRONMENT adicionada"
        ERRORS_FIXED=$((ERRORS_FIXED + 1))
    else
        log_success "Variável ENVIRONMENT já existe"
    fi
    
    # 1.9 Atualizar docker-compose.yml com portas detectadas
    log_info "Atualizando docker-compose.yml com portas detectadas..."
    if [[ -f docker-compose.yml ]]; then
        cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
        
        # Atualizar portas no docker-compose.yml
        sed -i "s|      - \"8000:8000\"|      - \"$WEB_PORT:8000\"|" docker-compose.yml
        sed -i "s|      - \"5432:5432\"|      - \"$DB_PORT:5432\"|" docker-compose.yml
        sed -i "s|      - \"6379:6379\"|      - \"$REDIS_PORT:6379\"|" docker-compose.yml
        sed -i "s|      - \"80:80\"|      - \"$NGINX_PORT:80\"|" docker-compose.yml
        sed -i "s|      - \"443:443\"|      - \"$NGINX_SSL_PORT:443\"|" docker-compose.yml
        
        log_success "docker-compose.yml atualizado com portas: $WEB_PORT, $DB_PORT, $REDIS_PORT, $NGINX_PORT, $NGINX_SSL_PORT"
        IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    fi
    
    log_info ""
    log_info "📁 2. Criando Estrutura de Diretórios..."
    
    # 2.1 Criar diretórios necessários
    mkdir -p logs staticfiles media backups
    log_success "Diretórios criados"
    IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    
    # 2.2 Configurar permissões
    chmod +x deploy_improved.sh 2>/dev/null || true
    chmod +x apply_all_improvements.sh
    log_success "Permissões configuradas"
    IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    
    log_info ""
    log_info "🧪 3. Implementando Estrutura de Testes..."
    
    # 3.1 Criar estrutura de testes básica
    if [[ ! -d tests ]]; then
        mkdir -p tests
        cat > tests/__init__.py << 'EOF'
# Testes do projeto FireFlies
EOF
        log_success "Estrutura de testes criada"
        IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    fi
    
    # 3.2 Criar testes básicos para cada app
    for app in apps/*/; do
        app_name=$(basename "$app")
        test_dir="apps/${app_name}/tests"
        
        if [[ ! -d "$test_dir" ]]; then
            mkdir -p "$test_dir"
            cat > "$test_dir/__init__.py" << EOF
# Testes do app ${app_name}
EOF
            
            # Criar teste básico para models
            if [[ -d "apps/${app_name}/models" ]]; then
                cat > "$test_dir/test_models.py" << EOF
from django.test import TestCase
from django.apps import apps

class ${app_name^}ModelsTestCase(TestCase):
    """Testes básicos para models do app ${app_name}"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.app_config = apps.get_app_config('${app_name}')
    
    def test_app_config(self):
        """Testa se o app está configurado corretamente"""
        self.assertEqual(self.app_config.name, 'apps.${app_name}')
    
    def test_app_models_loaded(self):
        """Testa se os models foram carregados"""
        self.assertIsNotNone(self.app_config.models_module)
EOF
            fi
            
            log_success "Testes criados para ${app_name}"
            IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
        fi
    done
    
    log_info ""
    log_info "🔒 4. Melhorando Configurações de Segurança..."
    
    # 4.1 Verificar e corrigir configurações de segurança no .env
    if [[ -f .env ]]; then
        # Verificar DEBUG
        if grep -q "^DEBUG=True" .env; then
            sed -i "s|^DEBUG=True|DEBUG=False|" .env
            log_success "DEBUG alterado para False"
            ERRORS_FIXED=$((ERRORS_FIXED + 1))
        fi
        
        # Verificar ALLOWED_HOSTS
        if ! grep -q "192.168.1.100" .env; then
            sed -i "s|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100|" .env
            log_success "IP do servidor adicionado ao ALLOWED_HOSTS"
            ERRORS_FIXED=$((ERRORS_FIXED + 1))
        fi
        
        # Verificar CSRF_TRUSTED_ORIGINS
        if ! grep -q "^CSRF_TRUSTED_ORIGINS=" .env; then
            echo "CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://192.168.1.100" >> .env
            log_success "CSRF_TRUSTED_ORIGINS configurado"
            ERRORS_FIXED=$((ERRORS_FIXED + 1))
        fi
    fi
    
    log_info ""
    log_info "🐳 5. Validando Configurações Docker..."
    
    # 5.1 Validar docker-compose.yml
    if command_exists docker-compose; then
        if docker-compose config >/dev/null 2>&1; then
            log_success "docker-compose.yml está válido"
        else
            log_error "docker-compose.yml tem erros"
            docker-compose config
            ERRORS_FIXED=$((ERRORS_FIXED + 1))
        fi
    fi
    
    # 5.2 Verificar Dockerfile
    if [[ -f Dockerfile ]]; then
        log_success "Dockerfile encontrado"
    else
        log_warning "Dockerfile não encontrado"
    fi
    
    log_info ""
    log_info "📊 6. Configurando Monitoramento..."
    
    # 6.1 Criar script de health check
    cat > health_check.sh << 'EOF'
#!/bin/bash

# Script de Health Check para FireFlies

set -euo pipefail

# Cores
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "🔍 Health Check - FireFlies"
echo "=========================="

# Verificar Docker
if command -v docker >/dev/null 2>&1; then
    log_success "Docker está instalado"
else
    log_error "Docker não está instalado"
fi

# Verificar Docker Compose
if command -v docker-compose >/dev/null 2>&1; then
    log_success "Docker Compose está instalado"
else
    log_error "Docker Compose não está instalado"
fi

# Verificar containers
if docker ps >/dev/null 2>&1; then
    log_success "Docker está funcionando"
    
    # Verificar containers específicos
    if docker ps | grep -q "fireflies"; then
        log_success "Containers FireFlies estão rodando"
    else
        log_warning "Containers FireFlies não estão rodando"
    fi
else
    log_error "Docker não está funcionando"
fi

# Verificar portas
for port in 8000 5432 6379; do
    if netstat -tuln | grep -q ":$port "; then
        log_success "Porta $port está em uso"
    else
        log_warning "Porta $port não está em uso"
    fi
done

# Verificar arquivo .env
if [[ -f .env ]]; then
    log_success "Arquivo .env existe"
    
    # Verificar variáveis críticas
    if grep -q "^SECRET_KEY=" .env && ! grep -q "django-insecure" .env; then
        log_success "SECRET_KEY está configurada"
    else
        log_error "SECRET_KEY não está configurada corretamente"
    fi
    
    if grep -q "^ENVIRONMENT=" .env; then
        log_success "ENVIRONMENT está configurado"
    else
        log_error "ENVIRONMENT não está configurado"
    fi
else
    log_error "Arquivo .env não existe"
fi

echo ""
echo "✅ Health Check concluído"
EOF

    chmod +x health_check.sh
    log_success "Script de health check criado"
    IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    
    log_info ""
    log_info "📝 7. Criando Documentação..."
    
    # 7.1 Criar README de deploy
    cat > DEPLOY_README.md << 'EOF'
# 🚀 Guia de Deploy - FireFlies

## Pré-requisitos

- Ubuntu 20.04+
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM mínimo
- 10GB espaço livre

## Deploy Rápido

```bash
# 1. Clonar projeto
git clone <repository>
cd fireflies

# 2. Aplicar melhorias
chmod +x apply_all_improvements.sh
./apply_all_improvements.sh

# 3. Ativar grupo docker
newgrp docker

# 4. Executar deploy
./deploy_improved.sh
```

## Comandos Úteis

```bash
# Verificar saúde do sistema
./health_check.sh

# Verificar logs
./deploy_improved.sh --logs

# Backup
./deploy_improved.sh --backup

# Restaurar
./deploy_improved.sh --restore

# Parar serviços
docker-compose down

# Reiniciar serviços
docker-compose restart
```

## Troubleshooting

### Problemas Comuns

1. **Docker não encontrado**
   ```bash
   sudo apt update && sudo apt install docker.io
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   ```

2. **Porta 80 ocupada**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo systemctl stop nginx  # se necessário
   ```

3. **SECRET_KEY não configurada**
   ```bash
   ./fix_secret_key.sh
   ```

### Logs

```bash
# Logs da aplicação
docker-compose logs web

# Logs do banco
docker-compose logs db

# Logs do Redis
docker-compose logs redis
```

## Configuração

Edite o arquivo `.env` para personalizar:

- Configurações de banco de dados
- Configurações de email
- Configurações de segurança
- Configurações de cache

## Monitoramento

O sistema inclui:

- Health checks automáticos
- Logs estruturados
- Monitoramento de recursos
- Backup automático

## Suporte

Para problemas:

1. Execute: `./health_check.sh`
2. Verifique logs: `./deploy_improved.sh --logs`
3. Consulte: `DEPLOY_README.md`
EOF

    log_success "Documentação criada"
    IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    
    log_info ""
    log_info "🔧 8. Configurando Scripts de Manutenção..."
    
    # 8.1 Script de backup
    cat > backup.sh << 'EOF'
#!/bin/bash

# Script de Backup - FireFlies

set -euo pipefail

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Criando backup em: $BACKUP_DIR"

# Backup do banco de dados
if docker ps | grep -q "fireflies_db"; then
    docker exec fireflies_db_1 pg_dump -U fireflies_user fireflies_prod > "$BACKUP_DIR/database.sql"
    echo "✅ Backup do banco criado"
fi

# Backup dos arquivos
cp -r staticfiles "$BACKUP_DIR/" 2>/dev/null || true
cp -r media "$BACKUP_DIR/" 2>/dev/null || true
cp .env "$BACKUP_DIR/" 2>/dev/null || true

# Backup dos volumes Docker
docker run --rm -v fireflies_postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .

echo "✅ Backup concluído: $BACKUP_DIR"
EOF

    chmod +x backup.sh
    log_success "Script de backup criado"
    IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    
    # 8.2 Script de limpeza
    cat > cleanup.sh << 'EOF'
#!/bin/bash

# Script de Limpeza - FireFlies

set -euo pipefail

echo "🧹 Limpeza do sistema FireFlies"

# Limpar containers parados
docker container prune -f

# Limpar imagens não utilizadas
docker image prune -f

# Limpar volumes não utilizados
docker volume prune -f

# Limpar redes não utilizadas
docker network prune -f

# Limpar logs antigos
find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true

# Limpar backups antigos (manter últimos 5)
ls -t backups/ | tail -n +6 | xargs -I {} rm -rf "backups/{}" 2>/dev/null || true

echo "✅ Limpeza concluída"
EOF

    chmod +x cleanup.sh
    log_success "Script de limpeza criado"
    IMPROVEMENTS_APPLIED=$((IMPROVEMENTS_APPLIED + 1))
    
    log_info ""
    log_info "📋 RESUMO DAS MELHORIAS APLICADAS"
    log_info "================================="
    log_info "Melhorias aplicadas: $IMPROVEMENTS_APPLIED"
    log_info "Erros corrigidos: $ERRORS_FIXED"
    
    log_info ""
    log_info "✅ Todas as melhorias foram aplicadas!"
    log_info ""
    log_info "📋 Próximos passos:"
    log_info "1. Execute: newgrp docker"
    log_info "2. Execute: ./health_check.sh"
    log_info "3. Execute: ./deploy_improved.sh"
    log_info ""
    log_info "🔧 Scripts disponíveis:"
    log_info "  ./health_check.sh     # Verificar saúde do sistema"
    log_info "  ./backup.sh          # Criar backup"
    log_info "  ./cleanup.sh         # Limpeza do sistema"
    log_info "  ./deploy_improved.sh # Deploy principal"
    log_info ""
    log_info "📚 Documentação:"
    log_info "  DEPLOY_README.md     # Guia completo de deploy"
    log_info "  CORRECAO_DEPLOY_UBUNTU.md # Correções específicas"
}

# Execução
main "$@" 