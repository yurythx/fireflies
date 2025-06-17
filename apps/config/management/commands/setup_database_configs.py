"""
Comando para criar configurações iniciais de banco de dados
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.config.models import DatabaseConfiguration


class Command(BaseCommand):
    help = 'Cria configurações iniciais de banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação mesmo se já existirem configurações',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Verificar se já existem configurações
        if DatabaseConfiguration.objects.exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    'Já existem configurações de banco. Use --force para sobrescrever.'
                )
            )
            return

        self.stdout.write('Criando configurações iniciais de banco de dados...')

        # Configuração SQLite (padrão para desenvolvimento)
        sqlite_config, created = DatabaseConfiguration.objects.get_or_create(
            name='SQLite Desenvolvimento',
            defaults={
                'description': 'Banco SQLite para desenvolvimento local',
                'engine': 'django.db.backends.sqlite3',
                'name_db': 'db.sqlite3',
                'host': '',
                'port': '',
                'user': '',
                'password': '',
                'is_default': True,
                'is_active': True,
                'options': {}
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Criada: {sqlite_config.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Já existe: {sqlite_config.name}')
            )

        # Configuração PostgreSQL (template para produção)
        postgres_config, created = DatabaseConfiguration.objects.get_or_create(
            name='PostgreSQL Produção',
            defaults={
                'description': 'Banco PostgreSQL para ambiente de produção',
                'engine': 'django.db.backends.postgresql',
                'name_db': 'havoc_prod',
                'host': 'localhost',
                'port': '5432',
                'user': 'postgres',
                'password': '',
                'is_default': False,
                'is_active': False,
                'options': {
                    'OPTIONS': {
                        'sslmode': 'prefer',
                    }
                }
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Criada: {postgres_config.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Já existe: {postgres_config.name}')
            )

        # Configuração MySQL (template)
        mysql_config, created = DatabaseConfiguration.objects.get_or_create(
            name='MySQL Local',
            defaults={
                'description': 'Banco MySQL para desenvolvimento ou produção',
                'engine': 'django.db.backends.mysql',
                'name_db': 'havoc_db',
                'host': 'localhost',
                'port': '3306',
                'user': 'root',
                'password': '',
                'is_default': False,
                'is_active': False,
                'options': {
                    'OPTIONS': {
                        'charset': 'utf8mb4',
                        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    }
                }
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Criada: {mysql_config.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Já existe: {mysql_config.name}')
            )

        # Configuração PostgreSQL Docker (template)
        postgres_docker_config, created = DatabaseConfiguration.objects.get_or_create(
            name='PostgreSQL Docker',
            defaults={
                'description': 'Banco PostgreSQL rodando em container Docker',
                'engine': 'django.db.backends.postgresql',
                'name_db': 'havoc',
                'host': 'db',  # Nome do serviço no docker-compose
                'port': '5432',
                'user': 'postgres',
                'password': 'postgres',
                'is_default': False,
                'is_active': False,
                'options': {}
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Criada: {postgres_docker_config.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Já existe: {postgres_docker_config.name}')
            )

        # Testar configuração padrão
        default_config = DatabaseConfiguration.objects.filter(is_default=True).first()
        if default_config:
            self.stdout.write(f'\nTestando configuração padrão: {default_config.name}')
            success, message = default_config.test_connection()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Teste de conexão: {message}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Teste de conexão: {message}')
                )

        # Resumo
        total_configs = DatabaseConfiguration.objects.count()
        active_configs = DatabaseConfiguration.objects.filter(is_active=True).count()
        default_config = DatabaseConfiguration.objects.filter(is_default=True).first()

        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMO DAS CONFIGURAÇÕES')
        self.stdout.write('='*50)
        self.stdout.write(f'Total de configurações: {total_configs}')
        self.stdout.write(f'Configurações ativas: {active_configs}')
        self.stdout.write(f'Configuração padrão: {default_config.name if default_config else "Nenhuma"}')
        
        self.stdout.write('\n📋 PRÓXIMOS PASSOS:')
        self.stdout.write('1. Acesse /admin/ para gerenciar as configurações')
        self.stdout.write('2. Ou acesse /config/banco-dados/ para interface amigável')
        self.stdout.write('3. Configure as credenciais dos bancos conforme necessário')
        self.stdout.write('4. Teste as conexões antes de ativar')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Configurações de banco criadas com sucesso!')
        )
