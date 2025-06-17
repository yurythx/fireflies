from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from apps.config.services.module_service import ModuleService
from apps.config.interfaces.middleware import IModuleAccessMiddleware, IModuleContextMiddleware, IModuleService
import logging

logger = logging.getLogger(__name__)


class ModuleAccessMiddleware(MiddlewareMixin, IModuleAccessMiddleware):
    """Middleware para controlar acesso aos módulos baseado na configuração"""
    
    def __init__(self, get_response, module_service: IModuleService = None):
        self.get_response = get_response
        # Injeção de dependência - usa service fornecido ou cria padrão
        self.module_service = module_service or ModuleService()
        super().__init__(get_response)
    
    def process_request(self, request):
        """Processa a requisição para verificar acesso ao módulo"""

        # URLs que sempre devem ser acessíveis
        exempt_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/register/',
            '/accounts/password-reset/',
            '/config/',  # Todo o painel de configuração
        ]

        # Verifica se a URL está na lista de exceções
        if self.is_path_exempt(request.path, exempt_paths):
            return None

        # Extrai o nome do app da URL
        app_name = self.extract_app_name(request.path)

        # Se não conseguir identificar o app, permite acesso
        if not app_name:
            return None

        # Verifica se o módulo está habilitado
        if not self.module_service.is_module_enabled(app_name):
            # Se for um módulo principal, algo está errado - log mas permite acesso
            if self.module_service.is_core_module(app_name):
                logger.error(f"Módulo principal {app_name} está desabilitado!")
                return None

            # Obtém informações do módulo para mensagem mais informativa
            module = self.module_service.get_module_by_name(app_name)
            module_display_name = module.display_name if module else app_name.title()

            # Módulo desabilitado, redireciona para home com mensagem
            messages.warning(
                request,
                f'O módulo "{module_display_name}" não está disponível no momento. '
                f'Entre em contato com o administrador se precisar acessar esta funcionalidade.'
            )
            return HttpResponseRedirect(reverse('pages:home'))

        return None
    
    def is_path_exempt(self, path: str, exempt_paths: list = None) -> bool:
        """Verifica se um caminho está isento de verificação"""
        if exempt_paths is None:
            exempt_paths = [
                '/admin/',
                '/static/',
                '/media/',
                '/accounts/login/',
                '/accounts/logout/',
                '/accounts/register/',
                '/accounts/password-reset/',
                '/config/',
            ]
        
        for exempt_path in exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False
    
    def extract_app_name(self, path: str) -> str:
        """Extrai o nome do app da URL"""
        # Remove a barra inicial e divide por barras
        path_parts = path.strip('/').split('/')

        if not path_parts or path_parts[0] == '':
            return 'pages'  # URL raiz pertence ao app pages

        # Mapeia URLs para nomes de apps
        url_to_app_mapping = {
            'accounts': 'apps.accounts',
            'config': 'apps.config',
            'artigos': 'apps.articles',
            'blog': 'blog',
            'shop': 'shop',
            'forum': 'forum',
        }

        first_part = path_parts[0]

        # Se a URL está no mapeamento, retorna o app correspondente
        if first_part in url_to_app_mapping:
            return url_to_app_mapping[first_part]

        # URLs que pertencem ao app pages (páginas estáticas e dinâmicas)
        pages_urls = [
            'sobre', 'contato', 'privacidade', 'termos', 'design-demo',
            'paginas', 'busca'
        ]

        if first_part in pages_urls:
            return 'apps.pages'

        # Se não está no mapeamento e não é uma URL conhecida do pages,
        # pode ser uma página dinâmica (slug) do pages
        # Vamos assumir que é pages por padrão para URLs não mapeadas
        return 'apps.pages'


class ModuleContextMiddleware(MiddlewareMixin, IModuleContextMiddleware):
    """Middleware para adicionar contexto de módulos aos templates"""
    
    def __init__(self, get_response, module_service: IModuleService = None):
        self.get_response = get_response
        # Injeção de dependência - usa service fornecido ou cria padrão
        self.module_service = module_service or ModuleService()
        super().__init__(get_response)
    
    def process_template_response(self, request, response):
        """Adiciona contexto de módulos ao template"""
        if hasattr(response, 'context_data') and response.context_data is not None:
            # Adiciona módulos disponíveis para o menu
            response.context_data['available_modules'] = self.get_menu_modules()
            
            # Adiciona informações do módulo atual
            current_app = self.get_current_app(request)
            if current_app:
                current_module = self.get_current_module(current_app)
                response.context_data['current_module'] = current_module
        
        return response
    
    def get_current_app(self, request) -> str:
        """Identifica o app atual baseado na URL"""
        if hasattr(request, 'resolver_match') and request.resolver_match:
            return getattr(request.resolver_match, 'app_name', None)
        return None
    
    def get_menu_modules(self) -> list:
        """Obtém módulos disponíveis para o menu"""
        return self.module_service.get_menu_modules()
    
    def get_current_module(self, app_name: str):
        """Obtém informações do módulo atual"""
        return self.module_service.get_module_by_name(app_name)
