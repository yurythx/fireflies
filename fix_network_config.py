#!/usr/bin/env python3
"""
Script para verificar e corrigir configurações de rede no Django
Resolve problemas de ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS e CORS
"""

import os
import sys
import socket
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

def get_server_info():
    """Obtém informações do servidor"""
    hostname = socket.gethostname()
    
    # Tentar obter IP local
    try:
        # Conectar a um endereço externo para descobrir o IP local
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    
    return {
        'hostname': hostname,
        'local_ip': local_ip,
        'localhost': 'localhost',
        'loopback': '127.0.0.1',
        'all_interfaces': '0.0.0.0'
    }

def check_allowed_hosts():
    """Verifica e corrige ALLOWED_HOSTS"""
    server_info = get_server_info()
    
    print("🔍 Verificando ALLOWED_HOSTS...")
    print(f"   Hostname: {server_info['hostname']}")
    print(f"   IP Local: {server_info['local_ip']}")
    
    current_allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
    if isinstance(current_allowed_hosts, str):
        current_allowed_hosts = current_allowed_hosts.split(',')
    
    print(f"   ALLOWED_HOSTS atual: {current_allowed_hosts}")
    
    # Hosts necessários
    required_hosts = [
        server_info['localhost'],
        server_info['loopback'],
        server_info['all_interfaces'],
        server_info['hostname'],
        server_info['local_ip']
    ]
    
    # Verificar hosts faltantes
    missing_hosts = []
    for host in required_hosts:
        if host not in current_allowed_hosts:
            missing_hosts.append(host)
    
    if missing_hosts:
        print(f"   ⚠️  Hosts faltando: {missing_hosts}")
        return False
    else:
        print("   ✅ ALLOWED_HOSTS está configurado corretamente")
        return True

def check_csrf_trusted_origins():
    """Verifica e corrige CSRF_TRUSTED_ORIGINS"""
    server_info = get_server_info()
    
    print("\n🔍 Verificando CSRF_TRUSTED_ORIGINS...")
    
    current_csrf_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
    if isinstance(current_csrf_origins, str):
        current_csrf_origins = current_csrf_origins.split(',')
    
    print(f"   CSRF_TRUSTED_ORIGINS atual: {current_csrf_origins}")
    
    # Origens necessárias (com porta 8000)
    required_origins = [
        f"http://{server_info['localhost']}:8000",
        f"http://{server_info['loopback']}:8000",
        f"http://{server_info['all_interfaces']}:8000",
        f"http://{server_info['hostname']}:8000",
        f"http://{server_info['local_ip']}:8000"
    ]
    
    # Verificar origens faltantes
    missing_origins = []
    for origin in required_origins:
        if origin not in current_csrf_origins:
            missing_origins.append(origin)
    
    if missing_origins:
        print(f"   ⚠️  Origens faltando: {missing_origins}")
        return False
    else:
        print("   ✅ CSRF_TRUSTED_ORIGINS está configurado corretamente")
        return True

def check_cors_settings():
    """Verifica configurações de CORS"""
    print("\n🔍 Verificando configurações de CORS...")
    
    # Verificar se django-cors-headers está instalado
    try:
        import corsheaders
        print("   ✅ django-cors-headers está instalado")
        
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if cors_origins:
            print(f"   CORS_ALLOWED_ORIGINS: {cors_origins}")
        else:
            print("   ⚠️  CORS_ALLOWED_ORIGINS não configurado")
            
        return True
    except ImportError:
        print("   ℹ️  django-cors-headers não está instalado (opcional)")
        return True

def check_security_headers():
    """Verifica headers de segurança"""
    print("\n🔍 Verificando headers de segurança...")
    
    security_settings = {
        'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', False),
        'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', False),
        'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', False),
        'SECURE_BROWSER_XSS_FILTER': getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False),
        'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
        'X_FRAME_OPTIONS': getattr(settings, 'X_FRAME_OPTIONS', 'SAMEORIGIN'),
    }
    
    for setting, value in security_settings.items():
        status = "✅" if value else "⚠️"
        print(f"   {status} {setting}: {value}")
    
    return True

def generate_env_fix():
    """Gera comandos para corrigir o .env"""
    server_info = get_server_info()
    
    print("\n🔧 Comandos para corrigir o .env:")
    print("=" * 50)
    
    # ALLOWED_HOSTS
    allowed_hosts = f"localhost,127.0.0.1,0.0.0.0,{server_info['hostname']},{server_info['local_ip']}"
    print(f"# Corrigir ALLOWED_HOSTS:")
    print(f"sed -i 's/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS={allowed_hosts}/' .env")
    
    # CSRF_TRUSTED_ORIGINS
    csrf_origins = f"http://localhost:8000,http://127.0.0.1:8000,http://0.0.0.0:8000,http://{server_info['hostname']}:8000,http://{server_info['local_ip']}:8000"
    print(f"\n# Corrigir CSRF_TRUSTED_ORIGINS:")
    print(f"sed -i 's/^CSRF_TRUSTED_ORIGINS=.*/CSRF_TRUSTED_ORIGINS={csrf_origins}/' .env")
    
    # Adicionar headers de segurança se não existirem
    print(f"\n# Adicionar headers de segurança:")
    print(f"echo 'SECURE_BROWSER_XSS_FILTER=True' >> .env")
    print(f"echo 'SECURE_CONTENT_TYPE_NOSNIFF=True' >> .env")
    print(f"echo 'X_FRAME_OPTIONS=DENY' >> .env")
    
    print("\n# Ou execute o deploy novamente:")
    print("./deploy_improved.sh")

def main():
    """Função principal"""
    print("🚀 Verificação de Configurações de Rede - FireFlies")
    print("=" * 60)
    
    # Verificar configurações
    allowed_hosts_ok = check_allowed_hosts()
    csrf_origins_ok = check_csrf_trusted_origins()
    cors_ok = check_cors_settings()
    security_ok = check_security_headers()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO:")
    print(f"   ALLOWED_HOSTS: {'✅ OK' if allowed_hosts_ok else '❌ PROBLEMA'}")
    print(f"   CSRF_TRUSTED_ORIGINS: {'✅ OK' if csrf_origins_ok else '❌ PROBLEMA'}")
    print(f"   CORS: {'✅ OK' if cors_ok else '❌ PROBLEMA'}")
    print(f"   Security Headers: {'✅ OK' if security_ok else '❌ PROBLEMA'}")
    
    if allowed_hosts_ok and csrf_origins_ok and cors_ok and security_ok:
        print("\n🎉 Todas as configurações estão corretas!")
        print("   A aplicação deve funcionar sem problemas de rede.")
        return 0
    else:
        print("\n⚠️  Foram encontrados problemas de configuração.")
        print("   Execute os comandos abaixo para corrigir:")
        generate_env_fix()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 