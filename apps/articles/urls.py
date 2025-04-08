from django.urls import path
from apps.articles import views

app_name = 'articles'

urlpatterns = [
    # Página inicial com a lista de artigos publicados
    path('', views.ArticleListView.as_view(), name='index_articles'),  
    
    # Detalhes de um artigo específico
    path('articles/<slug:slug>/', views.ArticleDetails.as_view(), name='article-details'),

    # Página para criar um novo artigo
    path('new/', views.ArticleCreate.as_view(), name='new_article'),
    
    # Página para editar um artigo existente
    path('edit/<slug:slug>/', views.ArticleUpdateView.as_view(), name='edit_article'),

    # Página para excluir um artigo
    path('delete/<slug:slug>/', views.ArticleDeleteView.as_view(), name='delete_article'),

    # Filtragem por categoria
    path('category/<slug:slug>/', views.CategoryListView.as_view(), name='category'),

    # Filtragem por tag
    path('tag/<slug:slug>/', views.TagListView.as_view(), name='tag'),

    # Página de busca de artigos
    path('search/', views.SearchListView.as_view(), name='search'),
]