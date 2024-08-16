
from django.shortcuts import redirect
from apps.articles.forms import ArticleForm
from apps.articles.models import Article
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import ListView, DeleteView, UpdateView, CreateView, DetailView

PER_PAGE = 20


class ArticleListView(ListView):
    template_name = 'articles/index_articles.html'
    queryset = Article.objects.get_published()
    paginate_by = PER_PAGE
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Home -'
        return context


class ArticleDetails(DetailView):
    
    template_name = 'articles/article-details.html'#direcionando para o template
    model = Article #model usado para preencher 

    context_object_name = 'article'

    
class ArticleCreate(CreateView):

    model = Article
    form_class = ArticleForm
    template_name = 'articles/new-article.html'
    success_url ="/"
    
            
class ArticleUpdateView(UpdateView):
    
    model = Article
    form_class = ArticleForm
    template_name = 'articles/update-article.html'
    success_url ="/"    


class CategoryListView(ArticleListView):
    allow_empty = False

    def get_queryset(self):
        return super().get_queryset().filter(
            category__slug=self.kwargs['slug']
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'{self.object_list[0].category.name} - Categoria'
        return ctx


class TagListView(ArticleListView):
    allow_empty = False

    def get_queryset(self):
        return super().get_queryset().filter(
            tags__slug=self.kwargs['slug']
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'{self.object_list[0].tags.first().name} - Tag -'
        return ctx


class SearchListView(ArticleListView):

    template_name = 'articles/search-list.html'#direcionando para o template

    def get_queryset(self):
        qs = super().get_queryset() #começa a fazer a busca

        search = self.request.GET.get('search') # usa o argumento search referenciado no html no label da busca

        if not search: # se a busca retornar vazia
            return qs # retorna qs vazio

        qs = qs.filter( # fazendo filtro no campo de busca

            # os campos abaixo fazem a busca pelos campo especificados no models

           Q(title__icontains=search) |
           Q(exerpt__icontains=search) |
           Q(content__icontains=search) 
           

        )

        return qs

class ArticleDeleteView(DeleteView):  
    model = Article  
    template_name = 'articles/delete-article.html'
    success_url ="/"




