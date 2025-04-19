# Importações essenciais
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
import logging

# Importações do seu projeto
from .models import Produto
from .forms import ProdutoForm  # Supondo que você tenha um ModelForm para Produto
#from core.utils import is_ajax  # Helper que verifica se a requisição é AJAX

# Logger para debugar erros ou informações úteis
logger = logging.getLogger(__name__)

def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

# Mixin para permitir que uma ListView retorne HTML parcial quando for uma requisição AJAX
class AjaxListMixin:
    partial_template_name = None  # Template parcial para AJAX

    def render_to_response(self, context, **response_kwargs):
        # Se for uma requisição AJAX e o template parcial estiver definido, usa ele
        if is_ajax(self.request) and self.partial_template_name:
            return render(self.request, self.partial_template_name, context)
        # Caso contrário, renderiza normalmente
        return super().render_to_response(context, **response_kwargs)


# Mixin para tornar uma CreateView/UpdateView/DeleteView compatível com AJAX
class AjaxFormMixin:
    template_name_ajax = None  # Template alternativo para AJAX

    # Se o formulário for inválido e for AJAX, retorna JSON com erros
    def form_invalid(self, form):
        if is_ajax(self.request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    # Se o formulário for válido, salva e retorna JSON (se AJAX) ou redireciona
    def form_valid(self, form):
        self.object = form.save()
        if is_ajax(self.request):
            return JsonResponse({'success': True, 'message': 'Operação realizada com sucesso!'})
        return super().form_valid(form)

    # Renderização GET customizada para AJAX (ex: formulário no modal)
    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            try:
                self.object = self.get_object()
            except AttributeError:
                self.object = None
            context = self.get_context_data()
            return render(request, self.template_name_ajax or self.template_name, context)
        return super().get(request, *args, **kwargs)
    
class ProdutoListView(AjaxListMixin, ListView):
    model = Produto
    template_name = 'produtos/lista_produtos.html'  # Template principal
    partial_template_name = 'produtos/lista_produtos.html'  # HTML parcial para AJAX
    context_object_name = 'produtos'
    paginate_by = 10  # Paginação

    def get_queryset(self):
        queryset = Produto.objects.filter(visivel=True).order_by('-data_cadastro')
        nome = self.request.GET.get('nome', '')
        sku = self.request.GET.get('sku', '')
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if sku:
            queryset = queryset.filter(sku__icontains=sku)
        return queryset

class ProdutoCreateView(AjaxFormMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/form_produto.html'  # Template normal
    template_name_ajax = 'produtos/form_produto.html'  # Template para modal/AJAX
    success_url = reverse_lazy('produtos:lista_produtos')

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)  # Salva produto
        messages.success(self.request, 'Produto criado com sucesso!')
        return response

class ProdutoUpdateView(AjaxFormMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/form_produto.html'
    template_name_ajax = 'produtos/form_produto.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('produtos:lista_produtos')

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return response

class ProdutoDetailView(DetailView):
    model = Produto
    template_name = 'produtos/detalhes_produto_modal.html'  # Usado em modais
    context_object_name = 'produto'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        if is_ajax(request):
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)


class ProdutoDeleteView(DeleteView):
    model = Produto
    template_name = 'produtos/confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('produtos:lista_produtos')

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Produto, slug=slug)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        if is_ajax(request):
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        nome = self.object.nome
        try:
            self.object.delete()
            messages.success(request, f'Produto "{nome}" excluído com sucesso!')
            if is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Produto excluído com sucesso!'})
            return redirect(self.success_url)
        except Exception as e:
            logger.error(f"Erro ao excluir produto {nome}: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Erro ao excluir o produto.'})