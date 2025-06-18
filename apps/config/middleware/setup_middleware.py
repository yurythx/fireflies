"""
Middleware para redirecionar para setup na primeira instalação
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from pathlib import Path
import re


class SetupMiddleware:
    """
    Middleware que redireciona para o setup wizard na primeira instalação
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que não devem ser redirecionadas
        self.exempt_urls = [
            '/config/setup/',
            '/config/setup/api/',
            '/health/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Verificar se é primeira instalação
        if self.is_first_installation():
            # Verificar se a URL atual não está na lista de exceções
            if not self.is_exempt_url(request.path):
                # Redirecionar para setup
                return redirect('config:setup_wizard')
        
        response = self.get_response(request)
        return response
    
    def is_first_installation(self):
        """Verifica se é primeira instalação"""
        first_install_file = Path(settings.BASE_DIR) / '.first_install'
        return first_install_file.exists()
    
    def is_exempt_url(self, path):
        """Verifica se a URL está na lista de exceções"""
        for exempt_url in self.exempt_urls:
            if path.startswith(exempt_url):
                return True
        return False 