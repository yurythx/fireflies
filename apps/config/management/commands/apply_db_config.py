"""
Comando para aplicar configuração de banco de dados via linha de comando
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.config.models.configuration_models import DatabaseConfiguration


class Command(BaseCommand):
    help = 'Aplica uma configuração de banco de dados como padrão e atualiza o .env'

    def add_arguments(self, parser):
        parser.add_argument(
            'config_id',
            type=int,
            help='ID da configuração de banco de dados'
        )
        parser.add_argument(
            '--update-env',
            action='store_true',
            help='Atualizar arquivo .env com a nova configuração'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar aplicação mesmo se houver erros'
        )

    def handle(self, *args, **options):
        config_id = options['config_id']
        update_env = options['update_env']
        force = options['force']

        try:
            # Buscar configuração
            config = DatabaseConfiguration.objects.get(pk=config_id)
        except DatabaseConfiguration.DoesNotExist:
            raise CommandError(f'Configuração com ID {config_id} não encontrada')

        self.stdout.write(
            self.style.WARNING(f'Aplicando configuração: {config.name}')
        )

        # Verificar se a configuração está ativa
        if not config.is_active:
            if not force:
                raise CommandError(
                    f'Configuração "{config.name}" está inativa. '
                    f'Use --force para aplicar mesmo assim.'
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Configuração inativa, mas aplicando devido ao --force')
                )

        # Testar conexão se possível
        if not force:
            self.stdout.write('Testando conexão...')
            success, message = config.test_connection()
            if not success:
                raise CommandError(f'Falha no teste de conexão: {message}')
            else:
                self.stdout.write(self.style.SUCCESS('✓ Conexão testada com sucesso'))

        try:
            with transaction.atomic():
                # Remover padrão atual
                current_default = DatabaseConfiguration.objects.filter(is_default=True).first()
                if current_default and current_default != config:
                    current_default.is_default = False
                    current_default.save()
                    self.stdout.write(
                        f'Removido padrão de: {current_default.name}'
                    )

                # Definir novo padrão
                config.is_default = True
                config.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Configuração "{config.name}" definida como padrão')
                )

                # Atualizar .env se solicitado
                if update_env:
                    self.stdout.write('Atualizando arquivo .env...')
                    success, message = config.update_env_file()
                    if success:
                        self.stdout.write(self.style.SUCCESS(f'✓ {message}'))
                    else:
                        if force:
                            self.stdout.write(self.style.WARNING(f'⚠ {message}'))
                        else:
                            raise CommandError(f'Erro ao atualizar .env: {message}')

        except Exception as e:
            raise CommandError(f'Erro ao aplicar configuração: {str(e)}')

        # Mostrar resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('CONFIGURAÇÃO APLICADA COM SUCESSO'))
        self.stdout.write('='*50)
        self.stdout.write(f'Nome: {config.name}')
        self.stdout.write(f'Engine: {config.engine}')
        self.stdout.write(f'Banco: {config.name_db}')
        if config.host:
            self.stdout.write(f'Host: {config.host}:{config.port}')
        self.stdout.write(f'Usuário: {config.user or "N/A"}')
        
        if update_env:
            self.stdout.write('\n' + self.style.WARNING('IMPORTANTE:'))
            self.stdout.write('Reinicie o servidor Django para aplicar as mudanças!')
        
        self.stdout.write('='*50)
