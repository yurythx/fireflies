from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    label = 'accounts'
    verbose_name = "Autenticação e Usuários"

    def ready(self):
        # Importa os signals quando o app estiver pronto
        import apps.accounts.signals