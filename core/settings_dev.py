"""
Configurações específicas para desenvolvimento
"""
from .settings import *

# Forçar DEBUG em desenvolvimento
DEBUG = True

# Configurações de arquivos estáticos para desenvolvimento (sem WhiteNoise)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Storage simples para desenvolvimento
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Middleware mínimo para desenvolvimento (sem middlewares customizados)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middlewares customizados comentados para debug
    # 'apps.accounts.middleware.RateLimitMiddleware',
    # 'apps.accounts.middleware.AccessControlMiddleware',
    # 'apps.accounts.middleware.SmartRedirectMiddleware',
    # 'apps.config.middleware.module_middleware.ModuleAccessMiddleware',
    # 'apps.config.middleware.module_middleware.ModuleContextMiddleware',
]

# Configurações de segurança relaxadas para desenvolvimento
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Hosts permitidos para desenvolvimento
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

# CSRF origins para desenvolvimento
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://0.0.0.0:8000',
]

# Configurações de cache simples para desenvolvimento
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Logging mais verboso para desenvolvimento
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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Desabilitar Sentry em desenvolvimento
SENTRY_DSN = ''

print("🔧 Usando configurações de DESENVOLVIMENTO")
print("📁 Arquivos estáticos: Django StaticFilesStorage")
print("🚫 WhiteNoise: DESABILITADO")
print("🔒 HTTPS: DESABILITADO")
print("📊 Cache: Local Memory")
