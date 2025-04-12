from django.urls import path
from .views import FornecedorListView, FornecedorCreateView, FornecedorUpdateView, FornecedorDeleteView

app_name = 'fornecedores'

urlpatterns = [
    path('', FornecedorListView.as_view(), name='lista_fornecedores'),
    path('novo/', FornecedorCreateView.as_view(), name='novo_fornecedor'),
    path('<slug:slug>/editar/', FornecedorUpdateView.as_view(), name='editar_fornecedor'),
    path('<slug:slug>/excluir/', FornecedorDeleteView.as_view(), name='excluir_fornecedor'),
]