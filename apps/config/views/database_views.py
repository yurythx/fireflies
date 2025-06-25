"""
Views para informações de banco de dados (somente leitura)
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import os
from pathlib import Path


def is_admin_user(user):
    """Verifica se o usuário é admin"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin_user)
def database_info(request):
    """Página de informações do banco de dados (somente leitura)"""
    
    # Obter informações do banco atual
    db_info = get_database_info()
    
    # Obter informações do arquivo .env
    env_info = get_env_database_info()
    
    # Testar conexão
    connection_status = test_database_connection()
    
    context = {
        'page_title': 'Informações do Banco de Dados',
        'page_description': 'Status e configurações atuais do banco de dados',
        'db_info': db_info,
        'env_info': env_info,
        'connection_status': connection_status,
        'breadcrumbs': [
            {'name': 'Configurações', 'url': '/config/'},
            {'name': 'Banco de Dados', 'url': None}
        ]
    }
    
    return render(request, 'config/database/info.html', context)


def get_database_info():
    """Obtém informações do banco de dados atual"""
    try:
        db_settings = settings.DATABASES['default']
        
        info = {
            'engine': db_settings.get('ENGINE', ''),
            'name': db_settings.get('NAME', ''),
            'host': db_settings.get('HOST', ''),
            'port': db_settings.get('PORT', ''),
            'user': db_settings.get('USER', ''),
            'is_sqlite': 'sqlite' in db_settings.get('ENGINE', '').lower(),
            'is_postgresql': 'postgresql' in db_settings.get('ENGINE', '').lower(),
            'is_mysql': 'mysql' in db_settings.get('ENGINE', '').lower(),
        }
        
        # Determinar tipo de banco
        if info['is_sqlite']:
            info['type'] = 'SQLite'
            info['file_path'] = info['name']
        elif info['is_postgresql']:
            info['type'] = 'PostgreSQL'
        elif info['is_mysql']:
            info['type'] = 'MySQL'
        else:
            info['type'] = 'Desconhecido'
            
        return info
        
    except Exception as e:
        return {
            'error': f'Erro ao obter informações do banco: {str(e)}',
            'type': 'Erro'
        }


def get_env_database_info():
    """Obtém informações do banco no arquivo .env"""
    try:
        env_file = Path(settings.BASE_DIR) / '.env'
        
        if not env_file.exists():
            return {'exists': False, 'message': 'Arquivo .env não encontrado'}
        
        env_content = env_file.read_text(encoding='utf-8')
        lines = env_content.split('\n')
        
        db_vars = {}
        for line in lines:
            if '=' in line and any(var in line for var in ['DB_', 'DATABASE_']):
                key, value = line.split('=', 1)
                db_vars[key.strip()] = value.strip()
        
        return {
            'exists': True,
            'variables': db_vars,
            'has_database_url': 'DATABASE_URL' in db_vars,
            'has_db_engine': 'DB_ENGINE' in db_vars,
        }
        
    except Exception as e:
        return {
            'exists': False,
            'error': f'Erro ao ler arquivo .env: {str(e)}'
        }


def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        # Testar conexão
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Obter informações adicionais
        db_info = {}
        
        if 'sqlite' in settings.DATABASES['default']['ENGINE'].lower():
            # Para SQLite, verificar se o arquivo existe
            db_file = settings.DATABASES['default']['NAME']
            db_info['file_exists'] = os.path.exists(db_file)
            db_info['file_size'] = os.path.getsize(db_file) if db_info['file_exists'] else 0
            
        elif 'postgresql' in settings.DATABASES['default']['ENGINE'].lower():
            # Para PostgreSQL, obter versão
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                db_info['version'] = version
                
        elif 'mysql' in settings.DATABASES['default']['ENGINE'].lower():
            # Para MySQL, obter versão
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                db_info['version'] = version
        
        return {
            'status': 'success',
            'message': 'Conexão bem-sucedida',
            'details': db_info
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro na conexão: {str(e)}',
            'details': {}
        }


@login_required
@user_passes_test(is_admin_user)
def database_connection_test_ajax(request):
    """Teste de conexão via AJAX"""
    if request.method == 'POST':
        status = test_database_connection()
        return JsonResponse(status)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405) 