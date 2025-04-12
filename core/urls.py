
from django.conf import settings

from django.contrib import admin
from django.urls import path, include  # add this
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    #path('accounts/', include('django.contrib.auth.urls')),
    path("", include("apps.authentication.urls")), # Auth routes - login / register

    
    path("", include("apps.pages.urls")),
    path("config/", include("apps.config.urls")),
    path("articles/", include("apps.articles.urls")),
     path("enderecos/", include("apps.enderecos.urls")),
    path("clientes/", include("apps.clientes.urls")),
    path('fornecedores/', include('apps.fornecedores.urls', namespace='fornecedores')),  # Namespace configurado!

path('tinymce/', include('tinymce.urls')),

]


    
   

    
    
    
    


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
