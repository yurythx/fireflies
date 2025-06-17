from django.urls import path
from django.views.generic import TemplateView
from apps.pages.views import (
    HomeView,
    AboutView,
    ContactView,
    PrivacyView,
    TermsView,
    PageDetailView,
    PageListView,
    PageSearchView,
)

app_name = 'pages'

urlpatterns = [
    # Página inicial
    path('', HomeView.as_view(), name='home'),

    # Páginas estáticas
    path('sobre/', AboutView.as_view(), name='about'),
    path('contato/', ContactView.as_view(), name='contact'),
    path('privacidade/', PrivacyView.as_view(), name='privacy'),
    path('termos/', TermsView.as_view(), name='terms'),

    # Demo do design Django
    path('design-demo/', TemplateView.as_view(template_name='pages/design-demo.html'), name='design_demo'),

    # Páginas dinâmicas
    path('paginas/', PageListView.as_view(), name='page_list'),
    path('busca/', PageSearchView.as_view(), name='search'),

    # Página dinâmica - DEVE SER A ÚLTIMA URL para não interferir com outras rotas
    path('pagina/<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
]
