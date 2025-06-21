from django.shortcuts import render
from django.views import View
from django.http import Http404
from apps.pages.services.page_service import PageService
from apps.pages.repositories.page_repository import DjangoPageRepository
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from apps.pages.models import Page
from apps.articles.models import Article
from apps.config.models import SystemConfiguration

class HomeView(View):
    """View para a página inicial"""
    
    def get(self, request):
        """Exibe a página inicial"""
        # Verificar se o setup foi concluído
        setup_completed = request.session.pop('setup_completed', False)
        
        # Inicializa service
        page_service = PageService(DjangoPageRepository())
        
        try:
            # Obtém a homepage
            homepage = page_service.get_homepage()
            
            if not homepage:
                # Se não há homepage, renderiza template padrão
                context = {
                    'page': None,
                    'is_homepage': True,
                    'meta_title': 'Bem-vindo ao FireFlies',
                    'meta_description': 'Sistema de gerenciamento de conteúdo moderno com arquitetura limpa',
                    'setup_completed': setup_completed,
                }
                return render(request, 'pages/home_default.html', context)
            
            # Incrementa contador de visualizações
            page_service.increment_page_views(homepage.id)
            
            # Obtém páginas populares para exibir na home
            popular_pages = page_service.get_popular_pages(limit=5)
            
            # Obtém páginas recentes
            recent_pages = page_service.get_published_pages()[:5]
            
            context = {
                'page': homepage,
                'is_homepage': True,
                'popular_pages': popular_pages,
                'recent_pages': recent_pages,
                'meta_title': homepage.seo_title,
                'meta_description': homepage.seo_description,
                'meta_keywords': homepage.meta_keywords,
                'setup_completed': setup_completed,
            }
            
            # Usa template personalizado se definido
            template = homepage.template if homepage.template else 'pages/home.html'
            
            return render(request, template, context)
            
        except Exception as e:
            # Em caso de erro, renderiza página padrão
            context = {
                'page': None,
                'is_homepage': True,
                'error': str(e),
                'meta_title': 'FireFlies - Sistema de Gerenciamento',
                'meta_description': 'Sistema de gerenciamento de conteúdo',
                'setup_completed': setup_completed,
            }
            return render(request, 'pages/home_default.html', context)

@login_required
def dashboard_view(request):
    """
    Dashboard para usuários logados
    """
    # Buscar configurações do sistema
    try:
        config = SystemConfiguration.objects.first()
        site_name = config.site_name if config else 'FireFlies'
    except:
        site_name = 'FireFlies'
    
    # Buscar páginas do usuário
    try:
        user_pages = Page.objects.filter(
            created_by=request.user,
            is_active=True
        ).order_by('-updated_at')[:5]
    except:
        user_pages = []
    
    # Buscar artigos do usuário
    try:
        user_articles = Article.objects.filter(
            author=request.user
        ).order_by('-created_at')[:5]
    except:
        user_articles = []
    
    # Estatísticas básicas
    try:
        total_pages = Page.objects.filter(is_active=True).count()
        total_articles = Article.objects.filter(is_published=True).count()
        recent_activity = Page.objects.filter(
            updated_at__gte=timezone.now() - timedelta(days=7)
        ).count()
    except:
        total_pages = 0
        total_articles = 0
        recent_activity = 0
    
    context = {
        'user_pages': user_pages,
        'user_articles': user_articles,
        'total_pages': total_pages,
        'total_articles': total_articles,
        'recent_activity': recent_activity,
        'meta_title': 'FireFlies - Sistema de Gerenciamento',
        'meta_description': 'Dashboard do sistema FireFlies',
        'site_name': site_name,
    }
    
    return render(request, 'pages/dashboard.html', context)
