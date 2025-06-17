"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .health_check import health_check, readiness_check, liveness_check

# Importar views de erro personalizadas
from apps.accounts.middleware import handle_403_error, handle_404_error

# URLs principais da aplicação
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('config/', include('apps.config.urls')),
    path('artigos/', include('apps.articles.urls')),
    path('tinymce/', include('tinymce.urls')),

    # Health checks
    path('health/', health_check, name='health_check'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/live/', liveness_check, name='liveness_check'),

    # Pages como app principal (DEVE SER O ÚLTIMO devido ao catch-all)
    path('', include('apps.pages.urls')),
]

# Views de erro personalizadas
handler403 = 'apps.accounts.middleware.handle_403_error'
handler404 = 'apps.accounts.middleware.handle_404_error'

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
