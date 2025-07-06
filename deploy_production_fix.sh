#!/bin/bash

# FireFlies - Script de Deploy para Produção com Correção de Migrações
# Resolve problemas de migração como o erro de coluna image_caption

set -e  # Para o script se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de log
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    error "Este script deve ser executado no diretório raiz do projeto FireFlies"
    exit 1
fi

# Verificar se o ambiente virtual está ativo
if [ -z "$VIRTUAL_ENV" ]; then
    warn "Ambiente virtual não detectado. Tentando ativar..."
    if [ -d "env" ]; then
        source env/bin/activate
        log "Ambiente virtual ativado"
    else
        error "Ambiente virtual não encontrado. Execute: python3 -m venv env"
        exit 1
    fi
fi

# Função para verificar status das migrações
check_migrations() {
    step "Verificando status das migrações..."
    
    # Verificar migrações pendentes
    python manage.py showmigrations --list | grep -E "\[ \]" || true
    
    # Verificar se há migrações não aplicadas
    PENDING_MIGRATIONS=$(python manage.py showmigrations --list | grep -c "\[ \]" || echo "0")
    
    if [ "$PENDING_MIGRATIONS" -gt 0 ]; then
        warn "Encontradas $PENDING_MIGRATIONS migrações pendentes"
        return 1
    else
        log "Todas as migrações estão aplicadas"
        return 0
    fi
}

# Função para aplicar migrações com segurança
apply_migrations() {
    step "Aplicando migrações..."
    
    # Fazer backup antes das migrações
    if [ -f "db.sqlite3" ]; then
        cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
        log "Backup do banco criado"
    fi
    
    # Aplicar migrações
    python manage.py migrate --noinput
    
    log "Migrações aplicadas com sucesso"
}

# Função para verificar problemas específicos
check_specific_issues() {
    step "Verificando problemas específicos..."
    
    # Verificar se a coluna image_caption existe
    python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"\"\"
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'articles_article' 
        AND column_name = 'image_caption'
    \"\"\")
    result = cursor.fetchone()
    if result:
        print('✅ Coluna image_caption existe')
    else:
        print('❌ Coluna image_caption NÃO existe')
        exit(1)
" || {
        error "Problema detectado: coluna image_caption não existe"
        return 1
    }
    
    log "Verificação de problemas específicos concluída"
    return 0
}

# Função para corrigir problemas específicos
fix_specific_issues() {
    step "Corrigindo problemas específicos..."
    
    # Executar script de correção
    if [ -f "fix_migration_production.py" ]; then
        log "Executando script de correção..."
        python fix_migration_production.py
    else
        warn "Script de correção não encontrado, tentando correção manual..."
        
        # Tentar aplicar migração específica
        python manage.py migrate articles 0003_article_image_caption --fake-initial || {
            warn "Migração falhou, tentando criar coluna manualmente..."
            
            # Criar coluna manualmente
            python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('ALTER TABLE articles_article ADD COLUMN image_caption VARCHAR(255) DEFAULT \"\" NOT NULL')
    print('✅ Coluna criada manualmente')
    
    # Marcar migração como aplicada
    with connection.cursor() as cursor:
        cursor.execute('\"\"\"INSERT INTO django_migrations (app, name, applied) VALUES (\"articles\", \"0003_article_image_caption\", NOW()) ON CONFLICT (app, name) DO NOTHING\"\"\"')
    print('✅ Migração marcada como aplicada')
    
except Exception as e:
    print(f'❌ Erro: {e}')
    exit(1)
"
        }
    fi
    
    log "Correção de problemas específicos concluída"
}

# Função para coletar arquivos estáticos
collect_static() {
    step "Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput
    log "Arquivos estáticos coletados"
}

# Função para verificar saúde da aplicação
health_check() {
    step "Verificando saúde da aplicação..."
    
    # Testar se o Django está funcionando
    python manage.py check --deploy || {
        error "Problemas de configuração detectados"
        return 1
    }
    
    # Testar conexão com banco
    python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Conexão com banco OK')
except Exception as e:
    print(f'❌ Erro na conexão com banco: {e}')
    exit(1)
" || {
        error "Problema na conexão com banco de dados"
        return 1
    }
    
    log "Verificação de saúde concluída"
    return 0
}

# Função para reiniciar serviços
restart_services() {
    step "Reiniciando serviços..."
    
    # Se estiver usando systemd
    if command -v systemctl >/dev/null 2>&1; then
        if systemctl is-active --quiet fireflies; then
            log "Reiniciando serviço fireflies..."
            sudo systemctl restart fireflies
        fi
    fi
    
    # Se estiver usando Docker
    if [ -f "docker-compose.yml" ] || [ -f "docker-compose.prod.yml" ]; then
        log "Reiniciando containers Docker..."
        docker-compose -f docker-compose.prod.yml restart web || docker-compose restart web || true
    fi
    
    log "Serviços reiniciados"
}

# Função principal
main() {
    echo "🦟 FireFlies - Deploy de Produção com Correção de Migrações"
    echo "=========================================================="
    
    # Verificar pré-requisitos
    step "Verificando pré-requisitos..."
    
    # Verificar Python
    if ! command -v python3 >/dev/null 2>&1; then
        error "Python3 não encontrado"
        exit 1
    fi
    
    # Verificar Django
    if ! python -c "import django" 2>/dev/null; then
        error "Django não encontrado. Instale as dependências: pip install -r requirements.txt"
        exit 1
    fi
    
    log "Pré-requisitos verificados"
    
    # Verificar saúde inicial
    health_check || {
        error "Problemas de saúde detectados antes do deploy"
        exit 1
    }
    
    # Verificar migrações
    if ! check_migrations; then
        warn "Migrações pendentes detectadas"
        
        # Perguntar se deve continuar
        read -p "Deseja aplicar as migrações? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            apply_migrations
        else
            error "Deploy cancelado pelo usuário"
            exit 1
        fi
    fi
    
    # Verificar problemas específicos
    if ! check_specific_issues; then
        warn "Problemas específicos detectados"
        fix_specific_issues
    fi
    
    # Coletar arquivos estáticos
    collect_static
    
    # Verificar saúde final
    health_check || {
        error "Problemas de saúde detectados após deploy"
        exit 1
    }
    
    # Reiniciar serviços
    restart_services
    
    echo ""
    echo "🎉 Deploy concluído com sucesso!"
    echo "✅ A aplicação deve estar funcionando normalmente"
    echo ""
    echo "📊 Para verificar o status:"
    echo "   - Logs: tail -f /var/log/fireflies.log"
    echo "   - Status: systemctl status fireflies"
    echo "   - Health: curl http://localhost:8000/health/"
    echo ""
}

# Executar função principal
main "$@" 