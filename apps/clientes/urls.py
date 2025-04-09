from django.urls import path
from django.contrib.auth import views as auth_views
from apps.clientes.views import ClienteListView, ClienteCreateView, ClienteDetailView, ClienteUpdateView

app_name = 'clientes'

urlpatterns = [
    # Login e Logout (autenticação)
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Cadastro do cliente
    path('new-cliente/', ClienteCreateView.as_view(), name='new-cliente'),  # Usando ClienteCreate para o cadastro
    path('new-cliente/sucesso/', ClienteCreateView.as_view(), name='cadastro_sucesso'),  # Sucesso após cadastro
    
    # Listagem de clientes
    path('list-clientes/', ClienteListView.as_view(), name='list-clientes'),  # Listar todos os clientes
    
    # Detalhes de um cliente específico
    path('cliente-details/<slug:slug>/', ClienteDetailView.as_view(), name='cliente-details'),  # Usando slug para identificar o cliente
    
    # Atualização de um cliente existente
    path('update-cliente/<slug:slug>/editar/', ClienteUpdateView.as_view(), name='update-cliente'),  # Editar um cliente específico
]