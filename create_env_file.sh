#!/bin/bash

# =============================================================================
# SCRIPT PARA CRIAR ARQUIVO .env PARA O FIREFLIES CMS
# =============================================================================

echo "🔧 Criando arquivo .env para o FireFlies CMS..."

# Gerar SECRET_KEY segura
SECRET_KEY=$(python -c "import secrets; print('django-insecure-' + secrets.token_urlsafe(50))")

# Criar arquivo .env
cat > .env << EOF
# =============================================================================
# FIREFLIES CMS - CONFIGURAÇÃO DE AMBIENTE
# =============================================================================

# Ambiente
ENVIRONMENT=production
DEBUG=False

# Configurações de Segurança
DJANGO_SECRET_KEY=${SECRET_KEY}
SECRET_KEY=${SECRET_KEY}

# Configurações de Host
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Configurações de Banco de Dados PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fireflies_prod
DB_USER=fireflies_user
DB_PASSWORD=fireflies_password
DB_HOST=db
DB_PORT=5432

# URL do banco de dados (formato Django)
DATABASE_URL=postgresql://fireflies_user:fireflies_password@db:5432/fireflies_prod

# Configurações de Cache Redis
REDIS_URL=redis://redis:6379/0

# Configurações de Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=587
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Configurações de Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,gif,webp
ALLOWED_DOCUMENT_EXTENSIONS=pdf,doc,docx,txt,rtf

# Configurações de Sessão
SESSION_COOKIE_AGE=86400
SESSION_EXPIRE_AT_BROWSER_CLOSE=False

# Configurações de Rate Limiting
RATELIMIT_ENABLE=True
RATELIMIT_USE_CACHE=default

# Configurações de Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/django.log

# Configurações de Performance
CACHE_TIMEOUT=300
STATICFILES_STORAGE=django.contrib.staticfiles.storage.StaticFilesStorage

# Configurações de SSL (para produção)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
EOF

echo "✅ Arquivo .env criado com sucesso!"
echo "📋 Conteúdo do arquivo .env:"
echo "=================================="
cat .env
echo "=================================="
echo ""
echo "🚀 Agora você pode executar o deploy com:"
echo "   docker-compose up -d" 