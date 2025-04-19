from django.urls import path
from .views import (
    FornecedorListView,
    FornecedorCreateView,
    FornecedorUpdateView,
    FornecedorDeleteView,
    FornecedorDetailView,
)

app_name = 'fornecedores'

urlpatterns = [
    path('', FornecedorListView.as_view(), name='lista_fornecedores'),
    
    path('detalhes/<slug:slug>/', FornecedorDetailView.as_view(), name='detalhes_fornecedor'),
    path('novo/', FornecedorCreateView.as_view(), name='novo_fornecedor'),
    path('<slug:slug>/editar/', FornecedorUpdateView.as_view(), name='editar_fornecedor'),
    path('excluir/<slug:slug>/', FornecedorDeleteView.as_view(), name='excluir_fornecedor'),
]