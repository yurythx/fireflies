#!/usr/bin/env python3
"""
Script para criar arquivo .env para o FireFlies CMS
"""

import secrets
import os

def create_env_file():
    """Cria o arquivo .env com as configurações necessárias"""
    
    print("🔧 Criando arquivo .env para o FireFlies CMS...")
    
    # Gerar SECRET_KEY segura
    secret_key = f"django-insecure-{secrets.token_urlsafe(50)}"
    
    # Conteúdo do arquivo .env
    env_content = f"""# =============================================================================
# FIREFLIES CMS - CONFIGURAÇÃO DE AMBIENTE
# =============================================================================

# Ambiente (production com SSL desabilitado)
ENVIRONMENT=production
DEBUG=False

# Configurações de Segurança
DJANGO_SECRET_KEY={secret_key}
SECRET_KEY={secret_key}

# Configurações de Host (liberado para todos os hosts)
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://0.0.0.0:8000

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

# Configurações de SSL (TODAS DESABILITADAS para permitir HTTP)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_PROXY_SSL_HEADER=
"""
    
    # Salvar no arquivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")
    print("📋 Conteúdo do arquivo .env:")
    print("==================================")
    with open('.env', 'r', encoding='utf-8') as f:
        print(f.read())
    print("==================================")
    print()
    print("🚀 Agora você pode executar o deploy com:")
    print("   docker-compose up -d")

if __name__ == "__main__":
    create_env_file() 