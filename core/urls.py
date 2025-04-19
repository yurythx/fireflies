
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib import admin
from django.urls import path, include  # add this
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    
    path('accounts/', include('apps.accounts.urls', namespace='accounts')), # Custom users app route

    path('password/', auth_views.PasswordResetView.as_view(), name='password'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path("", include("apps.authentication.urls")), # Auth routes - login / register

    
    path("", include("apps.pages.urls")),
    path("config/", include("apps.config.urls")),
    path("articles/", include("apps.articles.urls")),
    path("enderecos/", include("apps.enderecos.urls")),
    path("clientes/", include("apps.clientes.urls" , namespace='clientes')),
    path('fornecedores/', include('apps.fornecedores.urls', namespace='fornecedores')),
    path('produtos/', include('apps.produtos.urls', namespace='produtos')),
   

    path('tinymce/', include('tinymce.urls')),

]


    
   

    
    
    
    


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
