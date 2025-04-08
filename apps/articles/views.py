from django.contrib import messages  # Para mensagens de feedback
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from apps.articles.forms import ArticleForm, CommentForm
from apps.articles.models import Article, Comment
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import ListView, DeleteView, UpdateView, CreateView, DetailView

PER_PAGE = 6

class ArticleListView(ListView):
    """Exibe a lista de artigos publicados."""
    
    template_name = 'articles/index_articles.html'
    queryset = Article.objects.get_published()
    paginate_by = PER_PAGE
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        """Adiciona título à página de artigos."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Artigos - Página inicial'
        return context

class ArticleDetails(DetailView):
    """Exibe os detalhes de um artigo, incluindo comentários."""
    
    model = Article
    template_name = 'articles/article-details.html'
    context_object_name = 'article'

    def get_object(self):
        """Obtém o artigo usando o slug, ou gera um erro 404 se não encontrado."""
        slug = self.kwargs.get('slug')
        return get_object_or_404(Article, slug=slug)

    def get_context_data(self, **kwargs):
        """Adiciona os comentários e o formulário de comentários ao contexto."""
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('-created_at')
        context['comments_count'] = self.object.comments.count()
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        """Processa o envio de comentários via AJAX."""
        article = self.get_object()
        form = CommentForm(request.POST)
        parent_id = request.POST.get('parent_id')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article

            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                comment.parent = parent_comment

            comment.save()
            return JsonResponse({
                'success': True,
                'author_name': comment.author_name,
                'text': comment.text,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M')
            })
        else:
            return JsonResponse({'success': False, 'error': 'Erro ao postar comentário. Tente novamente.'})

class ArticleCreate(CreateView):
    """Cria um novo artigo."""
    
    model = Article
    form_class = ArticleForm
    template_name = 'articles/new-article.html'
    success_url = "/"

    def form_valid(self, form):
        """Adiciona uma mensagem de sucesso ao criar o artigo."""
        response = super().form_valid(form)
        messages.success(self.request, 'Artigo criado com sucesso!')
        return response

class ArticleUpdateView(UpdateView):
    """Atualiza um artigo existente."""
    
    model = Article
    form_class = ArticleForm
    template_name = 'articles/update-article.html'
    success_url = "/"

    def form_valid(self, form):
        """Adiciona uma mensagem de sucesso ao atualizar o artigo."""
        response = super().form_valid(form)
        messages.success(self.request, 'Artigo atualizado com sucesso!')
        return response

class CategoryListView(ArticleListView):
    """Exibe artigos filtrados por categoria."""
    
    allow_empty = False

    def get_queryset(self):
        """Retorna artigos filtrados pela categoria."""
        return super().get_queryset().filter(category__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        """Adiciona o título da categoria ao contexto."""
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'{self.object_list[0].category.name} - Categoria'
        return ctx

class TagListView(ArticleListView):
    """Exibe artigos filtrados por tag."""
    
    allow_empty = False

    def get_queryset(self):
        """Retorna artigos filtrados pela tag."""
        return super().get_queryset().filter(tags__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        """Adiciona o título da tag ao contexto."""
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'{self.object_list[0].tags.first().name} - Tag'
        return ctx

class SearchListView(ArticleListView):
    """Exibe artigos filtrados por busca."""
    
    template_name = 'articles/search-list.html'

    def get_queryset(self):
        """Retorna artigos que correspondem ao critério de busca."""
        qs = super().get_queryset()
        search = self.request.GET.get('search')

        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(content__icontains=search)
            )
        return qs

class ArticleDeleteView(DeleteView):
    """Exclui um artigo."""
    
    model = Article
    template_name = 'articles/delete-article.html'
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        """Exclui o artigo e exibe uma mensagem de sucesso."""
        messages.success(self.request, 'Artigo excluído com sucesso!')
        return super().delete(request, *args, **kwargs)