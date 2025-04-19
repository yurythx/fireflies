from django.urls import path
from .views import (
    CustomUserListView,
    CustomUserCreateView,
    CustomUserDetailView,
    CustomUserUpdateView,
    CustomUserDeleteView
)

app_name = 'apps.accounts'

urlpatterns = [
    path('', CustomUserListView.as_view(), name='lista_usuarios'),
    path('novo/', CustomUserCreateView.as_view(), name='novo_usuario'),
    path('<int:id>/', CustomUserDetailView.as_view(), name='detalhes_usuario'),
    path('<int:id>/editar/', CustomUserUpdateView.as_view(), name='editar_usuario'),
    path('<int:id>/excluir/', CustomUserDeleteView.as_view(), name='excluir_usuario'),
    
]