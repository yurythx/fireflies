from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.views import View
from django.db import connection
from django.conf import settings
from apps.config.services.system_config_service import AuditLogService
from apps.config.repositories.config_repository import DjangoAuditLogRepository
from apps.config.mixins import ConfigPermissionMixin, PermissionHelperMixin
import psutil
import platform
import sys
import os
import django
from datetime import datetime, timedelta

User = get_user_model()

class ConfigDashboardView(ConfigPermissionMixin, PermissionHelperMixin, View):
    """Dashboard principal do módulo de configuração com métricas do sistema"""
    template_name = 'config/dashboard.html'

    def get_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # Métricas de CPU e Memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Informações do sistema
            system_info = {
                'platform': platform.system(),
                'platform_version': platform.release(),
                'python_version': sys.version.split()[0],
                'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            }

            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': round(memory.used / (1024**3), 2),  # GB
                'memory_total': round(memory.total / (1024**3), 2),  # GB
                'disk_percent': disk.percent,
                'disk_used': round(disk.used / (1024**3), 2),  # GB
                'disk_total': round(disk.total / (1024**3), 2),  # GB
                'system_info': system_info,
            }
        except Exception:
            return None

    def get_database_metrics(self):
        """Coleta métricas do banco de dados"""
        try:
            with connection.cursor() as cursor:
                # Informações básicas do banco
                db_info = {
                    'engine': connection.vendor,
                    'name': connection.settings_dict.get('NAME', 'Unknown'),
                }

                # Contagem de tabelas (específico para cada banco)
                if connection.vendor == 'sqlite':
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]

                    # Tamanho do banco SQLite
                    db_path = connection.settings_dict.get('NAME')
                    if db_path and os.path.exists(db_path):
                        db_size = round(os.path.getsize(db_path) / (1024**2), 2)  # MB
                    else:
                        db_size = 0

                elif connection.vendor == 'postgresql':
                    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
                    table_count = cursor.fetchone()[0]

                    cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
                    db_size = cursor.fetchone()[0]

                else:
                    table_count = 0
                    db_size = 'Unknown'

                return {
                    'engine': db_info['engine'],
                    'name': db_info['name'],
                    'table_count': table_count,
                    'size': db_size,
                }
        except Exception:
            return None

    def get_email_config_status(self):
        """Verifica status da configuração de email"""
        try:
            email_host = getattr(settings, 'EMAIL_HOST', '')
            email_port = getattr(settings, 'EMAIL_PORT', 587)
            email_use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
            email_use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
            default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '')

            return {
                'email_host': email_host,
                'email_port': email_port,
                'email_use_tls': email_use_tls,
                'email_use_ssl': email_use_ssl,
                'default_from_email': default_from_email,
                'email_configured': bool(email_host and default_from_email),
            }
        except Exception:
            return {
                'email_configured': False,
                'email_host': 'Erro na configuração',
                'email_port': 'N/A',
                'email_use_tls': False,
                'email_use_ssl': False,
                'default_from_email': 'Não configurado',
            }

    def get_articles_count(self):
        """Conta artigos se o app estiver disponível"""
        try:
            from apps.articles.models import Article
            return Article.objects.count()
        except ImportError:
            return 0

    def get(self, request):
        """Exibe o dashboard com métricas do sistema"""
        # Estatísticas de usuários
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        total_groups = Group.objects.count()

        # Usuários recentes (últimos 7 dias)
        week_ago = datetime.now() - timedelta(days=7)
        recent_users = User.objects.filter(date_joined__gte=week_ago).count()

        # Métricas do sistema
        system_metrics = self.get_system_metrics()
        database_metrics = self.get_database_metrics()
        email_config = self.get_email_config_status()

        # Contagem de artigos
        total_articles = self.get_articles_count()

        context = {
            # Estatísticas de usuários
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'superusers': superusers,
            'total_groups': total_groups,
            'recent_users': recent_users,
            'total_articles': total_articles,

            # Métricas do sistema
            'system_metrics': system_metrics,
            'database_metrics': database_metrics,
            'django_version': django.get_version(),
            'debug_mode': settings.DEBUG,
            'cache_status': True,  # Implementar verificação real do cache

            # Configuração de email
            **email_config,
        }

        return render(request, self.template_name, context)
