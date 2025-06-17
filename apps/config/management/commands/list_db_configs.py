"""
Comando para listar configurações de banco de dados disponíveis
"""

from django.core.management.base import BaseCommand
from apps.config.models.configuration_models import DatabaseConfiguration
from django.utils import timezone


class Command(BaseCommand):
    help = 'Lista todas as configurações de banco de dados disponíveis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Mostrar apenas configurações ativas'
        )
        parser.add_argument(
            '--test-connections',
            action='store_true',
            help='Testar conexões de todas as configurações'
        )

    def handle(self, *args, **options):
        active_only = options['active_only']
        test_connections = options['test_connections']

        # Buscar configurações
        configs = DatabaseConfiguration.objects.all()
        if active_only:
            configs = configs.filter(is_active=True)

        configs = configs.order_by('-is_default', 'name')

        if not configs.exists():
            self.stdout.write(
                self.style.WARNING('Nenhuma configuração de banco de dados encontrada')
            )
            return

        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('CONFIGURAÇÕES DE BANCO DE DADOS'))
        self.stdout.write('='*80)

        for config in configs:
            # Status indicators
            status_indicators = []
            if config.is_default:
                status_indicators.append(self.style.SUCCESS('PADRÃO'))
            if config.is_active:
                status_indicators.append(self.style.SUCCESS('ATIVO'))
            else:
                status_indicators.append(self.style.ERROR('INATIVO'))

            # Header
            self.stdout.write(f'\n📊 ID: {config.pk} | {config.name}')
            if status_indicators:
                self.stdout.write(f'   Status: {" | ".join(status_indicators)}')

            # Details
            self.stdout.write(f'   Engine: {config.get_engine_display()}')
            self.stdout.write(f'   Banco: {config.name_db}')
            
            if config.host:
                self.stdout.write(f'   Host: {config.host}:{config.port}')
            
            if config.user:
                self.stdout.write(f'   Usuário: {config.user}')
            
            if config.description:
                self.stdout.write(f'   Descrição: {config.description}')

            # Timestamps
            self.stdout.write(f'   Criado: {config.created_at.strftime("%d/%m/%Y %H:%M")}')
            if config.updated_at != config.created_at:
                self.stdout.write(f'   Atualizado: {config.updated_at.strftime("%d/%m/%Y %H:%M")}')

            # Test connection if requested
            if test_connections:
                self.stdout.write('   Testando conexão...', ending='')
                success, message = config.test_connection()
                if success:
                    self.stdout.write(self.style.SUCCESS(' ✓ OK'))
                else:
                    self.stdout.write(self.style.ERROR(f' ✗ ERRO: {message}'))

            # Last test result
            if config.last_tested_at:
                test_status = '✓ OK' if config.last_test_result else '✗ ERRO'
                test_color = self.style.SUCCESS if config.last_test_result else self.style.ERROR
                self.stdout.write(f'   Último teste: {config.last_tested_at.strftime("%d/%m/%Y %H:%M")} - {test_color(test_status)}')

            self.stdout.write('-' * 60)

        # Summary
        total = configs.count()
        active = configs.filter(is_active=True).count()
        default = configs.filter(is_default=True).count()

        self.stdout.write(f'\n📈 RESUMO:')
        self.stdout.write(f'   Total: {total} configurações')
        self.stdout.write(f'   Ativas: {active} configurações')
        self.stdout.write(f'   Padrão: {default} configuração(ões)')

        if not active_only and active < total:
            inactive = total - active
            self.stdout.write(f'   Inativas: {inactive} configurações')

        # Commands help
        self.stdout.write(f'\n💡 COMANDOS ÚTEIS:')
        self.stdout.write(f'   Aplicar configuração: python manage.py apply_db_config <ID> --update-env')
        self.stdout.write(f'   Testar conexão: python manage.py test_db_config <ID>')
        self.stdout.write(f'   Criar configuração: Acesse /config/banco-dados/criar/')

        self.stdout.write('='*80)
