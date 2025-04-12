from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'clientes'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('clientes/', views.ClienteListView.as_view(), name='list-clientes'),
    path('clientes/novo/', views.ClienteCreateView.as_view(), name='new-cliente'),
    path('clientes/<slug:slug>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/<slug:slug>/editar/', views.ClienteUpdateView.as_view(), name='cliente_edit'),
    path('clientes/<slug:slug>/excluir/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
]
