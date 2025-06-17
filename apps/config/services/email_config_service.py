from django.conf import settings
from django.core.mail import get_connection
from apps.config.models import EmailConfiguration
from apps.config.repositories.config_repository import DjangoSystemConfigRepository
from apps.config.interfaces.services import IEmailConfigService
from apps.config.interfaces.repositories import ISystemConfigRepository
from django.contrib.auth import get_user_model
import logging
import os

User = get_user_model()
logger = logging.getLogger(__name__)


class DynamicEmailConfigService(IEmailConfigService):
    """Serviço para gerenciar configurações de email dinamicamente com aplicação em tempo real"""
    
    def __init__(self, config_repository: ISystemConfigRepository = None):
        self.current_config = None
        self.connection = None
        # Usa injeção de dependência para o repositório
        self.config_repository = config_repository or DjangoSystemConfigRepository()
    
    def get_active_config(self):
        """Retorna a configuração de email ativa do banco ou sistema"""
        try:
            # Primeiro tenta buscar do repositório de configurações
            try:
                config_value = self.config_repository.get_by_key('email_settings')
                if config_value:
                    return config_value
            except Exception:
                pass  # Configuração não existe no banco, usa fallback

            # Fallback para modelo EmailConfiguration
            email_config = EmailConfiguration.objects.filter(is_active=True).first()
            if email_config:
                return email_config.get_config_dict()

            # Último fallback para settings.py
            return self._get_settings_config()

        except Exception as e:
            logger.error(f'Erro ao obter configuração de email: {e}')
            return self._get_settings_config()
    
    def _get_settings_config(self):
        """Retorna configurações padrão do settings.py"""
        return {
            'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'),
            'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', ''),
            'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 587),
            'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', ''),
            'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
            'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', True),
            'EMAIL_USE_SSL': getattr(settings, 'EMAIL_USE_SSL', False),
            'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@havoc.com'),
            'EMAIL_TIMEOUT': getattr(settings, 'EMAIL_TIMEOUT', 30),
        }
    
    def get_connection(self, config=None):
        """Cria conexão de email com configurações específicas"""
        if config is None:
            config = self.get_active_config()
        
        return get_connection(
            backend=config['EMAIL_BACKEND'],
            host=config.get('EMAIL_HOST', ''),
            port=config.get('EMAIL_PORT', 587),
            username=config.get('EMAIL_HOST_USER', ''),
            password=config.get('EMAIL_HOST_PASSWORD', ''),
            use_tls=config.get('EMAIL_USE_TLS', True),
            use_ssl=config.get('EMAIL_USE_SSL', False),
            timeout=config.get('EMAIL_TIMEOUT', 30),
        )
    
    def test_connection(self, config=None):
        """Testa a conexão de email"""
        try:
            if config is None:
                config = self.get_active_config()
            
            # Se for backend de console/dummy, considera como válido
            backend = config.get('EMAIL_BACKEND', '')
            if 'console' in backend or 'dummy' in backend or 'locmem' in backend:
                return True, "Backend de desenvolvimento configurado corretamente!"
            
            # Para SMTP, testa a conexão real
            connection = self.get_connection(config)
            connection.open()
            connection.close()
            return True, "Conexão SMTP estabelecida com sucesso!"
            
        except Exception as e:
            logger.error(f'Erro ao testar conexão de email: {e}')
            return False, str(e)
    
    def apply_config_to_settings(self, config_dict):
        """Aplica configurações dinamicamente ao Django settings"""
        try:
            # Atualiza as configurações do Django em tempo de execução
            settings.EMAIL_BACKEND = config_dict['EMAIL_BACKEND']
            settings.EMAIL_HOST = config_dict.get('EMAIL_HOST', '')
            settings.EMAIL_PORT = config_dict.get('EMAIL_PORT', 587)
            settings.EMAIL_HOST_USER = config_dict.get('EMAIL_HOST_USER', '')
            settings.EMAIL_HOST_PASSWORD = config_dict.get('EMAIL_HOST_PASSWORD', '')
            settings.EMAIL_USE_TLS = config_dict.get('EMAIL_USE_TLS', True)
            settings.EMAIL_USE_SSL = config_dict.get('EMAIL_USE_SSL', False)
            settings.DEFAULT_FROM_EMAIL = config_dict.get('DEFAULT_FROM_EMAIL', 'noreply@havoc.com')
            settings.EMAIL_TIMEOUT = config_dict.get('EMAIL_TIMEOUT', 30)
            
            # Também atualiza variáveis de ambiente para persistência
            self._update_environment_variables(config_dict)
            
            logger.info('Configurações de email aplicadas dinamicamente')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao aplicar configurações de email: {e}')
            return False
    
    def _update_environment_variables(self, config_dict):
        """Atualiza variáveis de ambiente (para persistência entre reinicializações)"""
        try:
            env_mapping = {
                'EMAIL_BACKEND': 'EMAIL_BACKEND',
                'EMAIL_HOST': 'EMAIL_HOST',
                'EMAIL_PORT': 'EMAIL_PORT',
                'EMAIL_HOST_USER': 'EMAIL_HOST_USER',
                'EMAIL_HOST_PASSWORD': 'EMAIL_HOST_PASSWORD',
                'EMAIL_USE_TLS': 'EMAIL_USE_TLS',
                'EMAIL_USE_SSL': 'EMAIL_USE_SSL',
                'DEFAULT_FROM_EMAIL': 'DEFAULT_FROM_EMAIL',
                'EMAIL_TIMEOUT': 'EMAIL_TIMEOUT',
            }

            # Atualiza variáveis na memória
            for config_key, env_key in env_mapping.items():
                value = config_dict.get(config_key, '')
                if isinstance(value, bool):
                    value = 'True' if value else 'False'
                elif value is None:
                    value = ''
                os.environ[env_key] = str(value)

            # Atualiza arquivo .env
            self._update_env_file(config_dict, env_mapping)

            logger.info('Variáveis de ambiente de email atualizadas (memória e arquivo .env)')

        except Exception as e:
            logger.error(f'Erro ao atualizar variáveis de ambiente: {e}')

    def _update_env_file(self, config_dict, env_mapping):
        """Atualiza o arquivo .env com as configurações de email"""
        try:
            from pathlib import Path
            from django.conf import settings
            from datetime import datetime

            # Caminho para o arquivo .env
            env_path = Path(settings.BASE_DIR) / '.env'

            # Lê o conteúdo atual do .env
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            else:
                lines = []

            # Cria backup antes de modificar
            if env_path.exists():
                backup_path = Path(settings.BASE_DIR) / f'.env.backup.email.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                import shutil
                shutil.copy2(env_path, backup_path)
                logger.info(f'Backup do .env criado: {backup_path.name}')

            # Processa as linhas existentes
            updated_lines = []
            updated_keys = set()

            for line in lines:
                line_stripped = line.strip()

                # Se é uma linha de comentário ou vazia, mantém
                if not line_stripped or line_stripped.startswith('#'):
                    updated_lines.append(line)
                    continue

                # Se é uma variável
                if '=' in line_stripped:
                    key = line_stripped.split('=')[0].strip()

                    # Se é uma variável de email que estamos atualizando
                    if key in env_mapping.values():
                        # Encontra a chave de configuração correspondente
                        config_key = None
                        for ck, ek in env_mapping.items():
                            if ek == key:
                                config_key = ck
                                break

                        if config_key and config_key in config_dict:
                            value = config_dict[config_key]
                            if isinstance(value, bool):
                                value = 'True' if value else 'False'
                            elif value is None:
                                value = ''
                            
                            updated_lines.append(f'{key}={value}\n')
                            updated_keys.add(key)
                        else:
                            updated_lines.append(line)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            # Adiciona variáveis que não existiam
            for config_key, env_key in env_mapping.items():
                if env_key not in updated_keys and config_key in config_dict:
                    value = config_dict[config_key]
                    if isinstance(value, bool):
                        value = 'True' if value else 'False'
                    elif value is None:
                        value = ''
                    
                    updated_lines.append(f'{env_key}={value}\n')

            # Salva o arquivo atualizado
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            logger.info(f'Arquivo .env atualizado com configurações de email')

        except Exception as e:
            logger.error(f'Erro ao atualizar arquivo .env: {e}')
    
    def save_config(self, config_dict, user=None, description="Configuração de email"):
        """Salva configuração no repositório"""
        try:
            # Salva no repositório de configurações
            success = self.config_repository.set_config(
                'email_settings', 
                config_dict, 
                description=description,
                updated_by=user
            )
            
            if success:
                # Aplica as configurações
                self.apply_config_to_settings(config_dict)
                logger.info(f'Configuração de email salva por {user.email if user else "sistema"}')
                return True
            else:
                logger.error('Erro ao salvar configuração de email no repositório')
                return False
                
        except Exception as e:
            logger.error(f'Erro ao salvar configuração de email: {e}')
            return False
    
    def sync_config_to_env(self):
        """Sincroniza configuração do banco para variáveis de ambiente"""
        try:
            config = self.get_active_config()
            if config:
                self._update_environment_variables(config)
                logger.info('Configuração de email sincronizada com variáveis de ambiente')
                return True
            else:
                logger.warning('Nenhuma configuração de email ativa encontrada')
                return False
                
        except Exception as e:
            logger.error(f'Erro ao sincronizar configuração de email: {e}')
            return False
    
    def get_backend_info(self, backend_name):
        """Retorna informações sobre um backend específico"""
        backends = {
            'django.core.mail.backends.smtp.EmailBackend': {
                'name': 'SMTP',
                'description': 'Envio via servidor SMTP',
                'fields': ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'],
                'optional_fields': ['EMAIL_USE_TLS', 'EMAIL_USE_SSL', 'EMAIL_TIMEOUT'],
                'defaults': {
                    'EMAIL_PORT': 587,
                    'EMAIL_USE_TLS': True,
                    'EMAIL_USE_SSL': False,
                    'EMAIL_TIMEOUT': 30
                }
            },
            'django.core.mail.backends.console.EmailBackend': {
                'name': 'Console',
                'description': 'Exibe emails no console (desenvolvimento)',
                'fields': [],
                'optional_fields': [],
                'defaults': {}
            },
            'django.core.mail.backends.filebased.EmailBackend': {
                'name': 'Arquivo',
                'description': 'Salva emails em arquivos',
                'fields': ['EMAIL_FILE_PATH'],
                'optional_fields': [],
                'defaults': {}
            },
            'django.core.mail.backends.locmem.EmailBackend': {
                'name': 'Memória Local',
                'description': 'Armazena emails na memória (desenvolvimento)',
                'fields': [],
                'optional_fields': [],
                'defaults': {}
            }
        }
        
        return backends.get(backend_name, {
            'name': 'Desconhecido',
            'description': 'Backend não reconhecido',
            'fields': [],
            'optional_fields': [],
            'defaults': {}
        })
    
    def get_preset_configs(self):
        """Retorna configurações pré-definidas para provedores populares"""
        return {
            'gmail': {
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_HOST': 'smtp.gmail.com',
                'EMAIL_PORT': 587,
                'EMAIL_USE_TLS': True,
                'EMAIL_USE_SSL': False,
                'DEFAULT_FROM_EMAIL': 'seu-email@gmail.com',
                'description': 'Gmail SMTP'
            },
            'outlook': {
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_HOST': 'smtp-mail.outlook.com',
                'EMAIL_PORT': 587,
                'EMAIL_USE_TLS': True,
                'EMAIL_USE_SSL': False,
                'DEFAULT_FROM_EMAIL': 'seu-email@outlook.com',
                'description': 'Outlook/Hotmail SMTP'
            },
            'yahoo': {
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_HOST': 'smtp.mail.yahoo.com',
                'EMAIL_PORT': 587,
                'EMAIL_USE_TLS': True,
                'EMAIL_USE_SSL': False,
                'DEFAULT_FROM_EMAIL': 'seu-email@yahoo.com',
                'description': 'Yahoo Mail SMTP'
            },
            'sendgrid': {
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_HOST': 'smtp.sendgrid.net',
                'EMAIL_PORT': 587,
                'EMAIL_USE_TLS': True,
                'EMAIL_USE_SSL': False,
                'DEFAULT_FROM_EMAIL': 'noreply@seudominio.com',
                'description': 'SendGrid SMTP'
            },
            'amazon_ses': {
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_HOST': 'email-smtp.us-east-1.amazonaws.com',
                'EMAIL_PORT': 587,
                'EMAIL_USE_TLS': True,
                'EMAIL_USE_SSL': False,
                'DEFAULT_FROM_EMAIL': 'noreply@seudominio.com',
                'description': 'Amazon SES SMTP'
            },
            'console': {
                'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
                'DEFAULT_FROM_EMAIL': 'noreply@localhost',
                'description': 'Console (desenvolvimento)'
            },
            'file': {
                'EMAIL_BACKEND': 'django.core.mail.backends.filebased.EmailBackend',
                'EMAIL_FILE_PATH': '/tmp/django-mails',
                'DEFAULT_FROM_EMAIL': 'noreply@localhost',
                'description': 'Arquivo (desenvolvimento)'
            }
        }
