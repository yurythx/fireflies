from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.config.models import AppModuleConfiguration, SystemConfiguration
from apps.config.services.module_service import ModuleService

User = get_user_model()


class SystemConfigurationModelTest(TestCase):
    """Testes para o modelo SystemConfiguration"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True
        )

    def test_create_system_config(self):
        """Teste criação de configuração do sistema"""
        config = SystemConfiguration.objects.create(
            site_name='Havoc Test',
            site_description='Site de teste',
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(config.site_name, 'Havoc Test')
        self.assertEqual(config.site_description, 'Site de teste')
        self.assertTrue(config.is_active)

    def test_system_config_str_method(self):
        """Teste método __str__ da configuração"""
        config = SystemConfiguration.objects.create(
            site_name='Havoc Test',
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(str(config), 'Havoc Test')


class AppModuleConfigurationModelTest(TestCase):
    """Testes para o modelo AppModuleConfiguration"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True
        )

    def test_create_module_config(self):
        """Teste criação de configuração de módulo"""
        module = AppModuleConfiguration.objects.create(
            app_name='test_app',
            display_name='App de Teste',
            description='Aplicação de teste',
            is_enabled=True,
            is_core=False,
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(module.app_name, 'test_app')
        self.assertEqual(module.display_name, 'App de Teste')
        self.assertTrue(module.is_enabled)
        self.assertFalse(module.is_core)

    def test_module_config_str_method(self):
        """Teste método __str__ do módulo"""
        module = AppModuleConfiguration.objects.create(
            app_name='test_app',
            display_name='App de Teste',
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(str(module), 'App de Teste')

    def test_module_is_available(self):
        """Teste propriedade is_available"""
        module = AppModuleConfiguration.objects.create(
            app_name='test_app',
            display_name='App de Teste',
            is_enabled=True,
            status='active',
            created_by=self.user,
            updated_by=self.user
        )
        self.assertTrue(module.is_available)

        module.is_enabled = False
        module.save()
        self.assertFalse(module.is_available)


class ModuleServiceTest(TestCase):
    """Testes para o ModuleService"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True
        )
        self.module_service = ModuleService()
        self.module = AppModuleConfiguration.objects.create(
            app_name='test_app',
            display_name='App de Teste',
            is_enabled=True,
            is_core=False,
            created_by=self.user,
            updated_by=self.user
        )

    def test_get_enabled_modules(self):
        """Teste obter módulos habilitados"""
        enabled_modules = self.module_service.get_enabled_modules()
        self.assertIn(self.module, enabled_modules)

    def test_is_module_enabled(self):
        """Teste verificar se módulo está habilitado"""
        self.assertTrue(self.module_service.is_module_enabled('test_app'))
        self.assertFalse(self.module_service.is_module_enabled('nonexistent_app'))

    def test_enable_disable_module(self):
        """Teste habilitar/desabilitar módulo"""
        # Desabilita módulo
        success = self.module_service.disable_module('test_app', self.user)
        self.assertTrue(success)
        self.assertFalse(self.module_service.is_module_enabled('test_app'))

        # Habilita módulo
        success = self.module_service.enable_module('test_app', self.user)
        self.assertTrue(success)
        self.assertTrue(self.module_service.is_module_enabled('test_app'))

    def test_get_module_statistics(self):
        """Teste obter estatísticas dos módulos"""
        stats = self.module_service.get_module_statistics()
        self.assertIn('total', stats)
        self.assertIn('enabled', stats)
        self.assertIn('core', stats)
        self.assertIn('custom', stats)


class ConfigViewsTest(TestCase):
    """Testes para as views de configuração"""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='userpass123'
        )

    def test_dashboard_view_admin(self):
        """Teste dashboard para admin"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('config:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_dashboard_view_regular_user(self):
        """Teste dashboard para usuário comum"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('config:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect ou acesso negado

    def test_dashboard_view_anonymous(self):
        """Teste dashboard para usuário anônimo"""
        response = self.client.get(reverse('config:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect para login

    def test_module_list_view_admin(self):
        """Teste listagem de módulos para admin"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('config:module_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Módulos')

    def test_module_list_view_regular_user(self):
        """Teste listagem de módulos para usuário comum"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('config:module_list'))
        self.assertEqual(response.status_code, 302)  # Acesso negado


class MiddlewareTest(TestCase):
    """Testes para o middleware de módulos"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True
        )
        # Cria módulo desabilitado para teste
        AppModuleConfiguration.objects.create(
            app_name='articles',
            display_name='Artigos',
            is_enabled=False,
            is_core=False,
            url_pattern='artigos/',
            created_by=self.user,
            updated_by=self.user
        )

    def test_module_middleware_disabled_module(self):
        """Teste middleware com módulo desabilitado"""
        response = self.client.get('/artigos/')
        # Deve redirecionar para home com mensagem
        self.assertEqual(response.status_code, 302)

    def test_module_middleware_enabled_module(self):
        """Teste middleware com módulo habilitado"""
        # Habilita o módulo
        module = AppModuleConfiguration.objects.get(app_name='articles')
        module.is_enabled = True
        module.save()

        response = self.client.get('/artigos/')
        # Deve permitir acesso (200 ou 404 se a view não existir)
        self.assertIn(response.status_code, [200, 404])
