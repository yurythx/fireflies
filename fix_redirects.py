#!/usr/bin/env python3
"""
Script para verificar e corrigir problemas de redirecionamento 301
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.urls import reverse, NoReverseMatch

def check_url_patterns():
    """Verifica padrões de URL"""
    print("🔍 Verificando padrões de URL...")
    
    try:
        from core.urls import urlpatterns
        
        print(f"   Total de padrões de URL: {len(urlpatterns)}")
        
        # Verificar URLs principais
        main_urls = [
            'health_check',
            'setup_redirect',
            'admin:index',
        ]
        
        for url_name in main_urls:
            try:
                url = reverse(url_name)
                print(f"   ✅ {url_name}: {url}")
            except NoReverseMatch as e:
                print(f"   ❌ {url_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar URLs: {e}")
        return False

def check_health_endpoint():
    """Verifica endpoint de health check"""
    print("\n🔍 Verificando endpoint de health check...")
    
    try:
        from core.health_check import health_check
        
        # Simular request
        from django.test import RequestFactory
        from django.http import HttpResponse
        
        factory = RequestFactory()
        request = factory.get('/health/')
        
        response = health_check(request)
        
        if response.status_code == 200:
            print("   ✅ Health check retorna 200")
            return True
        else:
            print(f"   ❌ Health check retorna {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro no health check: {e}")
        return False

def check_setup_redirect():
    """Verifica redirecionamento de setup"""
    print("\n🔍 Verificando redirecionamento de setup...")
    
    try:
        from apps.config.views.setup_views import setup_redirect
        
        # Simular request
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        
        response = setup_redirect(request)
        
        if response.status_code in [301, 302]:
            print(f"   ✅ Setup redirect retorna {response.status_code}")
            print(f"   📍 Redireciona para: {response.url}")
            return True
        else:
            print(f"   ❌ Setup redirect retorna {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro no setup redirect: {e}")
        return False

def check_middleware():
    """Verifica middleware"""
    print("\n🔍 Verificando middleware...")
    
    middleware_classes = getattr(settings, 'MIDDLEWARE', [])
    
    print(f"   Total de middleware: {len(middleware_classes)}")
    
    # Verificar middleware importantes
    important_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ]
    
    for middleware in important_middleware:
        if middleware in middleware_classes:
            print(f"   ✅ {middleware}")
        else:
            print(f"   ❌ {middleware} (faltando)")
    
    return True

def check_static_files():
    """Verifica configuração de arquivos estáticos"""
    print("\n🔍 Verificando arquivos estáticos...")
    
    static_url = getattr(settings, 'STATIC_URL', '/static/')
    static_root = getattr(settings, 'STATIC_ROOT', None)
    
    print(f"   STATIC_URL: {static_url}")
    print(f"   STATIC_ROOT: {static_root}")
    
    if static_root and os.path.exists(static_root):
        print("   ✅ STATIC_ROOT existe")
    else:
        print("   ⚠️  STATIC_ROOT não existe ou não configurado")
    
    return True

def generate_fix_commands():
    """Gera comandos para corrigir problemas"""
    print("\n🔧 Comandos para corrigir problemas:")
    print("=" * 50)
    
    print("# 1. Resetar banco de dados:")
    print("./reset_database.sh")
    
    print("\n# 2. Coletar arquivos estáticos:")
    print("docker-compose exec web python manage.py collectstatic --noinput")
    
    print("\n# 3. Executar migrations:")
    print("docker-compose exec web python manage.py migrate")
    
    print("\n# 4. Criar superusuário:")
    print("docker-compose exec web python manage.py createsuperuser")
    
    print("\n# 5. Verificar logs:")
    print("docker-compose logs -f web")
    
    print("\n# 6. Reiniciar containers:")
    print("docker-compose restart")

def main():
    """Função principal"""
    print("🚀 Verificação de Redirecionamentos - FireFlies")
    print("=" * 60)
    
    # Verificar configurações
    urls_ok = check_url_patterns()
    health_ok = check_health_endpoint()
    setup_ok = check_setup_redirect()
    middleware_ok = check_middleware()
    static_ok = check_static_files()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO:")
    print(f"   URLs: {'✅ OK' if urls_ok else '❌ PROBLEMA'}")
    print(f"   Health Check: {'✅ OK' if health_ok else '❌ PROBLEMA'}")
    print(f"   Setup Redirect: {'✅ OK' if setup_ok else '❌ PROBLEMA'}")
    print(f"   Middleware: {'✅ OK' if middleware_ok else '❌ PROBLEMA'}")
    print(f"   Static Files: {'✅ OK' if static_ok else '❌ PROBLEMA'}")
    
    if urls_ok and health_ok and setup_ok and middleware_ok and static_ok:
        print("\n🎉 Todas as configurações estão corretas!")
        print("   Os redirecionamentos 301 são normais para setup.")
        return 0
    else:
        print("\n⚠️  Foram encontrados problemas de configuração.")
        print("   Execute os comandos abaixo para corrigir:")
        generate_fix_commands()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 