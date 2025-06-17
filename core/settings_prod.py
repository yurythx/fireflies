"""
Configurações de produção para o projeto FireFlies

Este arquivo contém as configurações específicas para o ambiente de produção.
As configurações base estão em settings.py.
"""

from .settings import *
import os

# =============================================================================
# CONFIGURAÇÕES BÁSICAS DE PRODUÇÃO
# =============================================================================

DEBUG = False
ENVIRONMENT = 'production'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError("ALLOWED_HOSTS environment variable is required in production")

# Domínios permitidos para CSRF
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
if not CSRF_TRUSTED_ORIGINS or CSRF_TRUSTED_ORIGINS == ['']:
    raise ValueError("CSRF_TRUSTED_ORIGINS environment variable is required in production")

# =============================================================================
# BANCO DE DADOS
# =============================================================================

# Usar a configuração dinâmica do settings principal
# A função get_database_config() já trata PostgreSQL, MySQL e SQLite corretamente
DATABASES = get_database_config()

# Apenas adicionar configurações específicas de produção se necessário
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    # Adicionar configurações específicas do PostgreSQL para produção
    DATABASES['default'].update({
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
        'OPTIONS': {
            'connect_timeout': 60,
            'options': '-c default_transaction_isolation=read_committed'
        }
    })
elif DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
    # Adicionar configurações específicas do MySQL para produção
    DATABASES['default'].update({
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    })
# Para SQLite, não adicionar nada - manter configuração limpa

# =============================================================================
# CACHE (OPCIONAL - REDIS)
# =============================================================================

REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
            },
            'KEY_PREFIX': 'fireflies',
            'TIMEOUT': 300,
        }
    }

    # Cache para sessões
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# =============================================================================
# ARQUIVOS ESTÁTICOS E MEDIA
# =============================================================================

# Arquivos estáticos
STATIC_ROOT = os.environ.get('STATIC_ROOT', '/app/staticfiles')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/app/media')

# =============================================================================
# SEGURANÇA
# =============================================================================

# HTTPS
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies seguros (apenas se HTTPS estiver habilitado)
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# HSTS (apenas se HTTPS estiver habilitado)
if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Outras configurações de segurança
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# LOGGING
# =============================================================================

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.environ.get('LOG_FILE', '/app/logs/django.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Adicionar handler de arquivo se especificado
if LOG_FILE:
    LOGGING['handlers']['file'] = {
        'level': LOG_LEVEL,
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOG_FILE,
        'maxBytes': 1024*1024*15,  # 15MB
        'backupCount': 10,
        'formatter': 'verbose',
    }
    LOGGING['root']['handlers'].append('file')
    LOGGING['loggers']['django']['handlers'].append('file')
    LOGGING['loggers']['apps']['handlers'].append('file')

# =============================================================================
# EMAIL
# =============================================================================

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@fireflies.com')

# =============================================================================
# SENTRY (MONITORAMENTO DE ERROS) - OPCIONAL
# =============================================================================

SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration(auto_enabling=True)],
            traces_sample_rate=0.1,
            send_default_pii=True,
            environment='production',
        )
    except ImportError:
        pass  # Sentry não instalado

# =============================================================================
# CONFIGURAÇÕES ESPECÍFICAS DO PROJETO
# =============================================================================

# Desabilitar debug toolbar em produção
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# Remover middleware de debug
MIDDLEWARE = [mw for mw in MIDDLEWARE if 'debug_toolbar' not in mw]

# Configurações de upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
