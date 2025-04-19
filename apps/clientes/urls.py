from django.urls import path
from .views import (
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDeleteView,
    ClienteDetailView,
)

app_name = 'clientes'

urlpatterns = [
    path('', ClienteListView.as_view(), name='lista_clientes'),
    
    path('detalhes/<slug:slug>/', ClienteDetailView.as_view(), name='detalhes_cliente'),
    path('novo/', ClienteCreateView.as_view(), name='novo_cliente'),
    path('<slug:slug>/editar/', ClienteUpdateView.as_view(), name='editar_cliente'),
    path('<slug:slug>/excluir/', ClienteDeleteView.as_view(), name='excluir_cliente')

    
]
