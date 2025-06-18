"""
Views para configuração pós-deploy do FireFlies
Similar ao Zabbix e GLPI, permite configurar banco de dados após primeira instalação
"""

import os
import json
import shutil
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
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
import psycopg2

# Importação condicional do MySQL
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception


class SetupWizardView(View):
    """
    Wizard de configuração pós-deploy
    """
    template_name = 'config/setup_wizard.html'
    
    def get(self, request):
        """Exibe o wizard de configuração"""
        # Verificar se já está configurado
        if not self.is_first_installation():
            messages.warning(request, "O sistema já está configurado!")
            return redirect('admin:index')
        
        context = {
            'step': request.GET.get('step', '1'),
            'current_step': int(request.GET.get('step', '1')),
            'total_steps': 4,
            'available_databases': self.detect_available_databases(),
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Processa a configuração"""
        step = request.POST.get('step', '1')
        
        if step == '1':
            return self.step_1_database_config(request)
        elif step == '2':
            return self.step_2_admin_user(request)
        elif step == '3':
            return self.step_3_email_config(request)
        elif step == '4':
            return self.step_4_finalize(request)
        
        return redirect('setup_wizard')
    
    def is_first_installation(self):
        """Verifica se é primeira instalação"""
        first_install_file = Path(settings.BASE_DIR) / '.first_install'
        return first_install_file.exists()
    
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
                            
                            # Verificar se é um banco Django (tem tabelas auth_user, django_migrations, etc.)
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
                    break  # Se encontrou uma instância, não precisa testar outras portas
                    
                except Exception:
                    # Tentar com usuário root
                    try:
                        conn = psycopg2.connect(
                            host=host,
                            port=port,
                            user='root',
                            password='',
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
                                    user='root',
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
                        break
                    except Exception:
                        continue
        
        return postgresql_instances
    
    def detect_mysql_databases(self):
        """Detecta bancos MySQL disponíveis"""
        mysql_instances = []
        
        # Verificar se MySQL está disponível
        if not MYSQL_AVAILABLE:
            return mysql_instances
        
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
                        connection_timeout=3
                    )
                    
                    cursor = conn.cursor()
                    cursor.execute("SHOW DATABASES;")
                    databases = cursor.fetchall()
                    
                    # Obter informações detalhadas de cada banco
                    detailed_databases = []
                    for db in databases:
                        db_name = db[0]
                        # Pular bancos do sistema
                        if db_name in ['information_schema', 'performance_schema', 'mysql', 'sys']:
                            continue
                            
                        try:
                            # Conectar ao banco específico para obter informações
                            db_conn = mysql.connector.connect(
                                host=host,
                                port=port,
                                user='root',
                                password='',
                                database=db_name,
                                connection_timeout=3
                            )
                            db_cursor = db_conn.cursor()
                            
                            # Contar tabelas
                            db_cursor.execute("SHOW TABLES;")
                            tables = db_cursor.fetchall()
                            tables_count = len(tables)
                            
                            # Obter tamanho do banco
                            db_cursor.execute("""
                                SELECT 
                                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'DB Size in MB'
                                FROM information_schema.tables 
                                WHERE table_schema = %s
                            """, (db_name,))
                            size_result = db_cursor.fetchone()
                            size = f"{size_result[0]} MB" if size_result and size_result[0] is not None else "N/A"
                            
                            # Verificar se é um banco Django (tem tabelas auth_user, django_migrations, etc.)
                            django_tables = ['auth_user', 'django_migrations', 'django_content_type']
                            db_cursor.execute("SHOW TABLES;")
                            all_tables_result = db_cursor.fetchall()
                            all_tables = [table[0] for table in all_tables_result if table and len(table) > 0]
                            django_table_count = sum(1 for table in django_tables if table in all_tables)
                            is_django = django_table_count >= 2
                            
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
                    break  # Se encontrou uma instância, não precisa testar outras portas
                    
                except Exception:
                    continue
        
        return mysql_instances
    
    def step_1_database_config(self, request):
        """Passo 1: Configuração do banco de dados"""
        print("DEBUG: step_1_database_config called")
        try:
            db_type = request.POST.get('db_type', 'sqlite')
            print(f"DEBUG: db_type = {db_type}")
            db_config = {}
            
            if db_type == 'postgresql':
                db_config = {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': request.POST.get('db_name'),
                    'USER': request.POST.get('db_user'),
                    'PASSWORD': request.POST.get('db_password'),
                    'HOST': request.POST.get('db_host', 'localhost'),
                    'PORT': request.POST.get('db_port', '5432'),
                }
                
                # Testar conexão PostgreSQL
                self.test_postgresql_connection(db_config)
                
            elif db_type == 'mysql':
                db_config = {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': request.POST.get('db_name'),
                    'USER': request.POST.get('db_user'),
                    'PASSWORD': request.POST.get('db_password'),
                    'HOST': request.POST.get('db_host', 'localhost'),
                    'PORT': request.POST.get('db_port', '3306'),
                }
                
                # Testar conexão MySQL
                self.test_mysql_connection(db_config)
                
            else:  # SQLite
                # Verificar se foi selecionado um banco existente
                existing_path = request.POST.get('existing_sqlite_path')
                print(f"DEBUG: existing_path = {existing_path}")
                if existing_path and Path(existing_path).exists():
                    # Usar banco existente
                    db_config = {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': existing_path,
                        'EXISTING_DATABASE': True,
                    }
                else:
                    # Criar novo banco
                    db_config = {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': Path(settings.BASE_DIR) / 'db.sqlite3',
                    }
            
            print(f"DEBUG: db_config = {db_config}")
            
            # Salvar configuração temporária
            self.save_temp_db_config(db_config)
            print("DEBUG: temp db config saved")
            
            messages.success(request, "Configuração do banco de dados salva com sucesso!")
            print("DEBUG: redirecting to step 2")
            return HttpResponseRedirect(reverse('config:setup_wizard') + '?step=2')
            
        except Exception as e:
            print(f"DEBUG: Exception in step_1_database_config: {str(e)}")
            messages.error(request, f"Erro na configuração do banco: {str(e)}")
            return HttpResponseRedirect(reverse('config:setup_wizard') + '?step=1')
    
    def step_2_admin_user(self, request):
        """Passo 2: Criação do usuário administrador"""
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            if not all([username, email, password, password_confirm]):
                raise ValueError("Todos os campos são obrigatórios")
            
            if password != password_confirm:
                raise ValueError("As senhas não coincidem")
            
            if len(password) < 8:
                raise ValueError("A senha deve ter pelo menos 8 caracteres")
            
            # Salvar dados do admin temporariamente
            admin_data = {
                'username': username,
                'email': email,
                'password': password,
            }
            self.save_temp_admin_config(admin_data)
            
            messages.success(request, "Dados do administrador salvos!")
            return HttpResponseRedirect(reverse('config:setup_wizard') + '?step=3')
            
        except Exception as e:
            messages.error(request, f"Erro na configuração do admin: {str(e)}")
            return HttpResponseRedirect(reverse('config:setup_wizard') + '?step=2')
    
    def step_3_email_config(self, request):
        """Passo 3: Configuração de email"""
        try:
            email_backend = request.POST.get('email_backend', 'smtp')
            
            if email_backend == 'smtp':
                email_config = {
                    'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                    'HOST': request.POST.get('email_host'),
                    'PORT': request.POST.get('email_port', '587'),
                    'USE_TLS': request.POST.get('email_use_tls') == 'on',
                    'USER': request.POST.get('email_user'),
                    'PASSWORD': request.POST.get('email_password'),
                }
            else:
                email_config = {
                    'BACKEND': 'django.core.mail.backends.console.EmailBackend',
                }
            
            # Salvar configuração de email temporariamente
            self.save_temp_email_config(email_config)
            
            messages.success(request, "Configuração de email salva!")
            return HttpResponseRedirect(reverse('config:setup_wizard') + '?step=4')
            
        except Exception as e:
            messages.error(request, f"Erro na configuração de email: {str(e)}")
            return HttpResponseRedirect(reverse('config:setup_wizard') + '?step=3')
    
    def step_4_finalize(self, request):
        """Passo 4: Finalizar configuração"""
        try:
            # Aplicar todas as configurações
            self.apply_all_configurations()
            
            # Remover arquivo de primeira instalação
            first_install_file = Path(settings.BASE_DIR) / '.first_install'
            if first_install_file.exists():
                first_install_file.unlink()
            
            # Limpar arquivos temporários
            self.cleanup_temp_files()
            
            messages.success(request, "Configuração concluída com sucesso! O sistema está pronto para uso.")
            return redirect('pages:home')
            
        except Exception as e:
            messages.error(request, f"Erro ao finalizar configuração: {str(e)}")
            return HttpResponseRedirect(reverse('config:setup_wizard') + '?step=4')
    
    def test_postgresql_connection(self, config):
        """Testa conexão com PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=config['HOST'],
                port=config['PORT'],
                database=config['NAME'],
                user=config['USER'],
                password=config['PASSWORD'],
                connect_timeout=10
            )
            conn.close()
        except Exception as e:
            raise ValueError(f"Falha na conexão com PostgreSQL: {str(e)}")
    
    def test_mysql_connection(self, config):
        """Testa conexão com MySQL"""
        if not MYSQL_AVAILABLE:
            raise ValueError("MySQL não está disponível. Instale mysql-connector-python para usar MySQL.")
        
        try:
            conn = mysql.connector.connect(
                host=config['HOST'],
                port=config['PORT'],
                database=config['NAME'],
                user=config['USER'],
                password=config['PASSWORD'],
                connection_timeout=10
            )
            conn.close()
        except MySQLError as e:
            raise ValueError(f"Falha na conexão com MySQL: {str(e)}")
    
    def save_temp_db_config(self, config):
        """Salva configuração de banco temporária"""
        temp_file = Path(settings.BASE_DIR) / '.temp_db_config.json'
        with open(temp_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def save_temp_admin_config(self, config):
        """Salva configuração de admin temporária"""
        temp_file = Path(settings.BASE_DIR) / '.temp_admin_config.json'
        with open(temp_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def save_temp_email_config(self, config):
        """Salva configuração de email temporária"""
        temp_file = Path(settings.BASE_DIR) / '.temp_email_config.json'
        with open(temp_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def apply_all_configurations(self):
        """Aplica todas as configurações salvas"""
        print("DEBUG: apply_all_configurations called")
        # Aplicar configuração de banco
        self.apply_database_config()
        
        # Executar migrations
        print("DEBUG: running migrations")
        # call_command('migrate', verbosity=0)
        
        # Aplicar configuração de admin
        self.apply_admin_config()
        
        # Aplicar configuração de email
        self.apply_email_config()
        
        # Coletar arquivos estáticos
        print("DEBUG: collecting static files")
        # call_command('collectstatic', '--noinput', verbosity=0)
    
    def apply_database_config(self):
        """Aplica configuração de banco de dados"""
        temp_file = Path(settings.BASE_DIR) / '.temp_db_config.json'
        if not temp_file.exists():
            return
        
        with open(temp_file, 'r') as f:
            db_config = json.load(f)
        
        # Atualizar .env com nova configuração
        env_file = Path(settings.BASE_DIR) / '.env'
        env_content = []
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.readlines()
        
        # Atualizar ou adicionar variáveis de banco
        db_vars = {
            'DATABASE_ENGINE': db_config['ENGINE'].split('.')[-1],
            'DB_NAME': db_config['NAME'],
            'DB_USER': db_config.get('USER', ''),
            'DB_PASSWORD': db_config.get('PASSWORD', ''),
            'DB_HOST': db_config.get('HOST', 'localhost'),
            'DB_PORT': db_config.get('PORT', ''),
        }
        
        for var, value in db_vars.items():
            found = False
            for i, line in enumerate(env_content):
                if line.startswith(f'{var}='):
                    env_content[i] = f'{var}={value}\n'
                    found = True
                    break
            if not found:
                env_content.append(f'{var}={value}\n')
        
        with open(env_file, 'w') as f:
            f.writelines(env_content)
    
    def apply_admin_config(self):
        """Aplica configuração de administrador"""
        temp_file = Path(settings.BASE_DIR) / '.temp_admin_config.json'
        if not temp_file.exists():
            return
        
        with open(temp_file, 'r') as f:
            admin_config = json.load(f)
        
        # Criar superusuário
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(username=admin_config['username']).exists():
            User.objects.create_superuser(
                username=admin_config['username'],
                email=admin_config['email'],
                password=admin_config['password']
            )
    
    def apply_email_config(self):
        """Aplica configuração de email"""
        temp_file = Path(settings.BASE_DIR) / '.temp_email_config.json'
        if not temp_file.exists():
            return
        
        with open(temp_file, 'r') as f:
            email_config = json.load(f)
        
        # Atualizar .env com configuração de email
        env_file = Path(settings.BASE_DIR) / '.env'
        env_content = []
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.readlines()
        
        email_vars = {
            'EMAIL_BACKEND': email_config['BACKEND'],
            'EMAIL_HOST': email_config.get('HOST', ''),
            'EMAIL_PORT': email_config.get('PORT', ''),
            'EMAIL_USE_TLS': str(email_config.get('USE_TLS', False)).lower(),
            'EMAIL_HOST_USER': email_config.get('USER', ''),
            'EMAIL_HOST_PASSWORD': email_config.get('PASSWORD', ''),
        }
        
        for var, value in email_vars.items():
            found = False
            for i, line in enumerate(env_content):
                if line.startswith(f'{var}='):
                    env_content[i] = f'{var}={value}\n'
                    found = True
                    break
            if not found:
                env_content.append(f'{var}={value}\n')
        
        with open(env_file, 'w') as f:
            f.writelines(env_content)
    
    def cleanup_temp_files(self):
        """Remove arquivos temporários"""
        temp_files = [
            '.temp_db_config.json',
            '.temp_admin_config.json',
            '.temp_email_config.json',
        ]
        
        for temp_file in temp_files:
            file_path = Path(settings.BASE_DIR) / temp_file
            if file_path.exists():
                file_path.unlink()


@method_decorator(csrf_exempt, name='dispatch')
class SetupAPIView(View):
    """
    API para configuração pós-deploy
    """
    
    def post(self, request):
        """API para testar conexões e salvar configurações"""
        try:
            action = request.POST.get('action')
            
            if action == 'test_database':
                return self.test_database_connection(request)
            elif action == 'save_config':
                return self.save_configuration(request)
            elif action == 'finalize':
                return self.finalize_setup(request)
            else:
                return JsonResponse({'error': 'Ação inválida'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def test_database_connection(self, request):
        """Testa conexão com banco de dados"""
        db_type = request.POST.get('db_type')
        
        try:
            if db_type == 'postgresql':
                conn = psycopg2.connect(
                    host=request.POST.get('db_host'),
                    port=request.POST.get('db_port', '5432'),
                    database=request.POST.get('db_name'),
                    user=request.POST.get('db_user'),
                    password=request.POST.get('db_password'),
                    connect_timeout=10
                )
                conn.close()
                
            elif db_type == 'mysql':
                if not MYSQL_AVAILABLE:
                    return JsonResponse({'error': 'MySQL não está disponível. Instale mysql-connector-python para usar MySQL.'}, status=400)
                
                conn = mysql.connector.connect(
                    host=request.POST.get('db_host'),
                    port=request.POST.get('db_port', '3306'),
                    database=request.POST.get('db_name'),
                    user=request.POST.get('db_user'),
                    password=request.POST.get('db_password'),
                    connection_timeout=10
                )
                conn.close()
                
            return JsonResponse({'success': True, 'message': 'Conexão bem-sucedida!'})
            
        except Exception as e:
            return JsonResponse({'error': f'Falha na conexão: {str(e)}'}, status=400)
    
    def save_configuration(self, request):
        """Salva configuração temporária"""
        config_type = request.POST.get('config_type')
        
        try:
            if config_type == 'database':
                config = {
                    'ENGINE': request.POST.get('db_engine'),
                    'NAME': request.POST.get('db_name'),
                    'USER': request.POST.get('db_user'),
                    'PASSWORD': request.POST.get('db_password'),
                    'HOST': request.POST.get('db_host'),
                    'PORT': request.POST.get('db_port'),
                }
                
                temp_file = Path(settings.BASE_DIR) / '.temp_db_config.json'
                with open(temp_file, 'w') as f:
                    json.dump(config, f, indent=2)
                    
            return JsonResponse({'success': True, 'message': 'Configuração salva!'})
            
        except Exception as e:
            return JsonResponse({'error': f'Erro ao salvar: {str(e)}'}, status=500)
    
    def finalize_setup(self, request):
        """Finaliza a configuração"""
        try:
            # Aplicar configurações
            wizard = SetupWizardView()
            wizard.apply_all_configurations()
            
            # Limpar arquivos temporários
            wizard.cleanup_temp_files()
            
            # Remover arquivo de primeira instalação
            first_install_file = Path(settings.BASE_DIR) / '.first_install'
            if first_install_file.exists():
                first_install_file.unlink()
            
            return JsonResponse({'success': True, 'message': 'Configuração finalizada!'})
            
        except Exception as e:
            return JsonResponse({'error': f'Erro ao finalizar: {str(e)}'}, status=500)


@never_cache
def setup_redirect(request):
    """
    Redireciona para setup se for primeira instalação
    """
    first_install_file = Path(settings.BASE_DIR) / '.first_install'
    
    if first_install_file.exists():
        return redirect('setup_wizard')
    else:
        return redirect('pages:home')  # Redireciona para a página inicial do app pages 