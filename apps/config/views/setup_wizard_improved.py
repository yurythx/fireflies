"""
Wizard de Configuração Melhorado - FireFlies
Versão otimizada com melhor UX e validações robustas
"""

import os
import json
import shutil
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Any
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.db import connections, connection
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from django.core.cache import cache
import psycopg2
import logging
from .setup_wizard.step_database import process_step as process_step_database
from .setup_wizard.step_admin import process_step_admin
from .setup_wizard.step_email import process_step_email
from .setup_wizard.step_security import process_step_security
from .setup_wizard.step_finalize import process_step_finalize

# Importação condicional do MySQL
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

logger = logging.getLogger(__name__)


class ImprovedSetupWizardViewZZZZZZ(View):
    """
    Wizard de configuração melhorado com UX otimizada
    """
    template_name = 'config/setup_wizard_improved.html'
    
    def get(self, request):
        print("DEBUG: ENTROU NA VIEW DO WIZARD!")
        progress = self.get_saved_progress()
        context = {
            'step': request.GET.get('step', '1'),
            'current_step': int(request.GET.get('step', '1')),
            'total_steps': 5,
            'progress': progress,
            'available_databases': self.detect_available_databases(),
            'system_info': self.get_system_info(),
            'recommendations': self.get_recommendations(),
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Processa a configuração"""
        step = request.POST.get('step', '1')
        try:
            if step == '1':
                return process_step_database(request, self)
            elif step == '2':
                return process_step_admin(request, self)
            elif step == '3':
                return process_step_email(request, self)
            elif step == '4':
                return process_step_security(request, self)
            elif step == '5':
                return process_step_finalize(request, self)
            return redirect('setup_wizard')
        except Exception as e:
            logger.error(f"Erro no wizard: {e}", exc_info=True)
            messages.error(request, f"Erro durante a configuração: {str(e)}")
            return redirect('setup_wizard')
    
    def is_first_installation(self):
        """Verifica se é primeira instalação"""
        first_install_file = Path(settings.BASE_DIR) / '.first_install'
        return first_install_file.exists()
    
    def get_saved_progress(self) -> Dict[str, Any]:
        """Obtém progresso salvo do cache"""
        return cache.get('setup_wizard_progress', {})
    
    def save_progress(self, step: str, data: Dict[str, Any]):
        """Salva progresso no cache"""
        progress = self.get_saved_progress()
        progress[step] = data
        cache.set('setup_wizard_progress', progress, timeout=3600)  # 1 hora
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtém informações do sistema"""
        import platform
        import psutil
        
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'django_version': settings.VERSION,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_usage': psutil.disk_usage('/'),
            'network_interfaces': self.get_network_interfaces(),
        }
    
    def get_network_interfaces(self) -> List[Dict[str, str]]:
        """Obtém interfaces de rede"""
        import psutil
        import socket
        
        interfaces = []
        for interface, addresses in psutil.net_if_addrs().items():
            for addr in addresses:
                if addr.family == socket.AF_INET:  # IPv4
                    interfaces.append({
                        'name': interface,
                        'ip': addr.address,
                        'netmask': addr.netmask,
                    })
        return interfaces
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Obtém recomendações baseadas no sistema"""
        system_info = self.get_system_info()
        recommendations = {
            'database': 'sqlite',  # Padrão
            'email_backend': 'console',
            'security_level': 'standard',
        }
        
        # Recomendações baseadas no sistema
        if system_info['memory_total'] > 4 * 1024 * 1024 * 1024:  # > 4GB
            recommendations['database'] = 'postgresql'
        
        if system_info['os'] == 'Linux':
            recommendations['security_level'] = 'enhanced'
        
        return recommendations
    
    def detect_available_databases(self):
        """Detecta bancos de dados disponíveis no sistema"""
        available = {
            'sqlite': self.detect_sqlite_databases(),
            'postgresql': self.detect_postgresql_databases(),
            'mysql': self.detect_mysql_databases(),
        }
        return available
    
    def detect_sqlite_databases(self):
        """Detecta bancos SQLite existentes"""
        sqlite_files = []
        base_dir = Path(settings.BASE_DIR)
        
        # Procurar por arquivos .sqlite3 e .db
        for pattern in ['*.sqlite3', '*.db', '*.sqlite']:
            for file_path in base_dir.rglob(pattern):
                if file_path.is_file():
                    try:
                        # Tentar conectar para verificar se é um banco válido
                        import sqlite3
                        conn = sqlite3.connect(str(file_path))
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        tables = cursor.fetchall()
                        conn.close()
                        
                        sqlite_files.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'relative_path': str(file_path.relative_to(base_dir)),
                            'size': file_path.stat().st_size,
                            'tables_count': len(tables),
                            'is_valid': True,
                            'last_modified': timezone.datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ),
                        })
                    except Exception:
                        # Se não conseguir conectar, pode não ser um banco válido
                        pass
        
        return sqlite_files
    
    def detect_postgresql_databases(self):
        """Detecta bancos PostgreSQL disponíveis"""
        postgresql_instances = []
        
        # Verificar se PostgreSQL está rodando em portas comuns
        common_ports = [5432, 5433, 5434]
        common_hosts = ['localhost', '127.0.0.1']
        
        for host in common_hosts:
            for port in common_ports:
                try:
                    # Tentar conectar sem especificar banco
                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        user='postgres',  # Usuário padrão
                        password='',  # Sem senha para teste
                        connect_timeout=3
                    )
                    
                    cursor = conn.cursor()
                    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                    databases = cursor.fetchall()
                    
                    # Obter informações detalhadas de cada banco
                    detailed_databases = []
                    for db in databases:
                        db_name = db[0]
                        try:
                            # Conectar ao banco específico para obter informações
                            db_conn = psycopg2.connect(
                                host=host,
                                port=port,
                                user='postgres',
                                password='',
                                database=db_name,
                                connect_timeout=3
                            )
                            db_cursor = db_conn.cursor()
                            
                            # Contar tabelas
                            db_cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
                            tables_count_result = db_cursor.fetchone()
                            tables_count = tables_count_result[0] if tables_count_result else 0
                            
                            # Obter tamanho do banco
                            db_cursor.execute("SELECT pg_size_pretty(pg_database_size(%s));", (db_name,))
                            size_result = db_cursor.fetchone()
                            size = size_result[0] if size_result else 'N/A'
                            
                            # Verificar se é um banco Django
                            db_cursor.execute("""
                                SELECT COUNT(*) FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name IN ('auth_user', 'django_migrations', 'django_content_type')
                            """)
                            django_tables_result = db_cursor.fetchone()
                            django_tables = django_tables_result[0] if django_tables_result else 0
                            is_django = django_tables >= 2
                            
                            db_conn.close()
                            
                            detailed_databases.append({
                                'name': db_name,
                                'tables_count': tables_count,
                                'size': size,
                                'is_django': is_django,
                                'is_valid': True,
                            })
                            
                        except Exception:
                            # Se não conseguir conectar ao banco específico, adicionar sem detalhes
                            detailed_databases.append({
                                'name': db_name,
                                'tables_count': 0,
                                'size': 'N/A',
                                'is_django': False,
                                'is_valid': False,
                            })
                    
                    conn.close()
                    
                    postgresql_instances.append({
                        'host': host,
                        'port': port,
                        'databases': detailed_databases,
                        'is_accessible': True,
                    })
                    
                except Exception:
                    # PostgreSQL não está rodando nesta porta
                    continue
        
        return postgresql_instances
    
    def detect_mysql_databases(self):
        """Detecta bancos MySQL disponíveis"""
        if not MYSQL_AVAILABLE:
            return []
        
        mysql_instances = []
        
        # Verificar se MySQL está rodando em portas comuns
        common_ports = [3306, 3307, 3308]
        common_hosts = ['localhost', '127.0.0.1']
        
        for host in common_hosts:
            for port in common_ports:
                try:
                    # Tentar conectar sem especificar banco
                    conn = mysql.connector.connect(
                        host=host,
                        port=port,
                        user='root',  # Usuário padrão
                        password='',  # Sem senha para teste
                        connect_timeout=3
                    )
                    
                    cursor = conn.cursor()
                    cursor.execute("SHOW DATABASES;")
                    databases = cursor.fetchall()
                    
                    # Obter informações detalhadas de cada banco
                    detailed_databases = []
                    for db in databases:
                        db_name = db[0]
                        try:
                            # Conectar ao banco específico para obter informações
                            db_conn = mysql.connector.connect(
                                host=host,
                                port=port,
                                user='root',
                                password='',
                                database=db_name,
                                connect_timeout=3
                            )
                            db_cursor = db_conn.cursor()
                            
                            # Contar tabelas
                            db_cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s;", (db_name,))
                            tables_count_result = db_cursor.fetchone()
                            tables_count = tables_count_result[0] if tables_count_result else 0
                            
                            # Obter tamanho do banco
                            db_cursor.execute("""
                                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
                                FROM information_schema.tables 
                                WHERE table_schema = %s
                            """, (db_name,))
                            size_result = db_cursor.fetchone()
                            size = f"{size_result[0]} MB" if size_result and size_result[0] else 'N/A'
                            
                            # Verificar se é um banco Django
                            db_cursor.execute("""
                                SELECT COUNT(*) FROM information_schema.tables 
                                WHERE table_schema = %s 
                                AND table_name IN ('auth_user', 'django_migrations', 'django_content_type')
                            """, (db_name,))
                            django_tables_result = db_cursor.fetchone()
                            django_tables = django_tables_result[0] if django_tables_result else 0
                            is_django = django_tables >= 2
                            
                            db_conn.close()
                            
                            detailed_databases.append({
                                'name': db_name,
                                'tables_count': tables_count,
                                'size': size,
                                'is_django': is_django,
                                'is_valid': True,
                            })
                            
                        except Exception:
                            # Se não conseguir conectar ao banco específico, adicionar sem detalhes
                            detailed_databases.append({
                                'name': db_name,
                                'tables_count': 0,
                                'size': 'N/A',
                                'is_django': False,
                                'is_valid': False,
                            })
                    
                    conn.close()
                    
                    mysql_instances.append({
                        'host': host,
                        'port': port,
                        'databases': detailed_databases,
                        'is_accessible': True,
                    })
                    
                except Exception:
                    # MySQL não está rodando nesta porta
                    continue
        
        return mysql_instances
    
    def test_database_connection(self, config):
        """Testa conexão com banco de dados"""
        try:
            if config['type'] == 'sqlite':
                return self.test_sqlite_connection(config)
            elif config['type'] == 'postgresql':
                return self.test_postgresql_connection(config)
            elif config['type'] == 'mysql':
                return self.test_mysql_connection(config)
            else:
                return False
        except Exception as e:
            logger.error(f"Erro no teste de conexão: {e}")
            return False
    
    def test_sqlite_connection(self, config):
        """Testa conexão SQLite"""
        try:
            import sqlite3
            db_path = config.get('path', 'db.sqlite3')
            conn = sqlite3.connect(db_path)
            conn.close()
            return True
        except Exception:
            return False
    
    def test_postgresql_connection(self, config):
        """Testa conexão PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                user=config.get('user', 'postgres'),
                password=config.get('password', ''),
                database=config.get('database', 'postgres'),
                connect_timeout=5
            )
            conn.close()
            return True
        except Exception:
            return False
    
    def test_mysql_connection(self, config):
        """Testa conexão MySQL"""
        if not MYSQL_AVAILABLE:
            return False
        
        try:
            conn = mysql.connector.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 3306),
                user=config.get('user', 'root'),
                password=config.get('password', ''),
                database=config.get('database', ''),
                connect_timeout=5
            )
            conn.close()
            return True
        except Exception:
            return False
    
    def apply_all_configurations(self):
        """Aplica todas as configurações salvas"""
        try:
            progress = self.get_saved_progress()
            
            # Aplicar configuração do banco
            if 'database' in progress:
                self.apply_database_config(progress['database'])
            
            # Aplicar configuração do admin
            if 'admin' in progress:
                self.apply_admin_config(progress['admin'])
            
            # Aplicar configuração de email
            if 'email' in progress:
                self.apply_email_config(progress['email'])
            
            # Aplicar configuração de segurança
            if 'security' in progress:
                self.apply_security_config(progress['security'])
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao aplicar configurações: {e}", exc_info=True)
            return False
    
    def apply_database_config(self, config):
        """Aplica configuração do banco de dados"""
        # Implementar aplicação da configuração do banco
        pass
    
    def apply_admin_config(self, config):
        """Aplica configuração do administrador"""
        # Implementar criação do usuário administrador
        pass
    
    def apply_email_config(self, config):
        """Aplica configuração de email"""
        # Implementar aplicação da configuração de email
        pass
    
    def apply_security_config(self, config):
        """Aplica configuração de segurança"""
        # Implementar aplicação da configuração de segurança
        pass


@method_decorator(csrf_exempt, name='dispatch')
class SetupAPIView(View):
    """API para o wizard de configuração"""
    
    def post(self, request):
        """Processa requisições da API"""
        action = request.POST.get('action')
        
        if action == 'test_connection':
            return self.test_database_connection(request)
        elif action == 'save_config':
            return self.save_configuration(request)
        elif action == 'finalize':
            return self.finalize_setup(request)
        else:
            return JsonResponse({'error': 'Ação inválida'}, status=400)
    
    def test_database_connection(self, request):
        """Testa conexão com banco de dados via API"""
        try:
            config_data = request.POST.get('config', '{}')
            config = json.loads(config_data)
            
            wizard = ImprovedSetupWizardViewZZZZZZ()
            success = wizard.test_database_connection(config)
            
            return JsonResponse({
                'success': success,
                'message': 'Conexão bem-sucedida' if success else 'Falha na conexão'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def save_configuration(self, request):
        """Salva configuração via API"""
        try:
            step = request.POST.get('step')
            config_data = request.POST.get('config', '{}')
            config = json.loads(config_data)
            
            wizard = ImprovedSetupWizardViewZZZZZZ()
            wizard.save_progress(step, config)
            
            return JsonResponse({
                'success': True,
                'message': 'Configuração salva com sucesso'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def finalize_setup(self, request):
        """Finaliza configuração via API"""
        try:
            wizard = ImprovedSetupWizardViewZZZZZZ()
            success = wizard.apply_all_configurations()
            
            if success:
                # Limpar cache de progresso
                cache.delete('setup_wizard_progress')
                
                # Remover arquivo de primeira instalação
                first_install_file = Path(settings.BASE_DIR) / '.first_install'
                if first_install_file.exists():
                    first_install_file.unlink()
            
            return JsonResponse({
                'success': success,
                'message': 'Configuração finalizada com sucesso' if success else 'Erro na finalização'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@never_cache
def setup_redirect(request):
    """Redireciona para o wizard se necessário"""
    wizard = ImprovedSetupWizardViewZZZZZZ()
    
    if wizard.is_first_installation():
        return redirect('setup_wizard_teste')
    else:
        return redirect('admin:index') 