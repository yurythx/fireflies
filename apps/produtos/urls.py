from django.urls import path
from . import views

app_name = 'apps.produtos'  # Namespace para reverses como 'produtos:criar_produto'

urlpatterns = [
    # Lista de produtos (com suporte a AJAX + filtro)
    path('', views.ProdutoListView.as_view(), name='lista_produtos'),

    # Criação de produto
    path('novo/', views.ProdutoCreateView.as_view(), name='criar_produto'),

    # Detalhes (usado em modal ou página)
    path('<slug:slug>/detalhes/', views.ProdutoDetailView.as_view(), name='detalhes_produto'),

    # Edição de produto
    path('<slug:slug>/editar/', views.ProdutoUpdateView.as_view(), name='editar_produto'),

    # Exclusão de produto
    path('<slug:slug>/excluir/', views.ProdutoDeleteView.as_view(), name='excluir_produto'),

]