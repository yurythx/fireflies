from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Fornecedor
from .forms import FornecedorForm


# Função utilitária para detectar se a requisição é AJAX (ex: carregamento de modal)
def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


# View para listar todos os fornecedores
class FornecedorListView(ListView):
    model = Fornecedor
    template_name = 'fornecedores/lista.html'
    context_object_name = 'fornecedores'  # Nome da variável de contexto usada no template


# Mixin reutilizável que adiciona suporte para requisições AJAX (modal)
class AjaxFormMixin:
    """
    Mixin que permite suporte AJAX para CreateView, UpdateView e DeleteView.
    Renderiza templates modais em requisições AJAX e responde com JSON.
    """
    template_name_ajax = None  # Template alternativo a ser usado quando a requisição for AJAX

    def form_invalid(self, form):
        # Retorna erros de formulário em formato JSON, se for uma requisição AJAX
        if is_ajax(self.request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        # Se for uma DeleteView, o form não tem save(), então chamamos delete diretamente
        if isinstance(self, DeleteView):
            return self.delete(self.request)
        
        # Para Create/Update, salva o objeto normalmente
        self.object = form.save()

        # Em caso de AJAX, retorna resposta JSON indicando sucesso
        if is_ajax(self.request):
            return JsonResponse({'success': True})

        # Caso contrário, segue o fluxo normal da view
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX, usa template alternativo para modal
        if is_ajax(request):
            try:
                # Pega o objeto, se a view tiver `get_object()` (Update/Delete)
                self.object = self.get_object()
            except AttributeError:
                self.object = None  # Em CreateView, não há objeto ainda

            context = self.get_context_data()
            return render(request, self.template_name_ajax, context)

        # Requisição padrão (não AJAX)
        return super().get(request, *args, **kwargs)


# View para criar um novo fornecedor (suporte AJAX incluído via mixin)
class FornecedorCreateView(AjaxFormMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    success_url = reverse_lazy('fornecedores:lista_fornecedores')
    template_name = 'fornecedores/fornecedor_form.html'
    template_name_ajax = 'fornecedores/form_modal.html'  # Modal usado com AJAX


# View para editar um fornecedor existente
class FornecedorUpdateView(AjaxFormMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    success_url = reverse_lazy('fornecedores:lista_fornecedores')
    template_name = 'fornecedores/fornecedor_form.html'
    template_name_ajax = 'fornecedores/form_modal.html'
    slug_field = 'slug'               # Campo usado na URL para identificar o objeto
    slug_url_kwarg = 'slug'           # Nome do parâmetro capturado na URL


# View para excluir um fornecedor (com confirmação via modal AJAX)
class FornecedorDeleteView(AjaxFormMixin, DeleteView):
    model = Fornecedor
    success_url = reverse_lazy('fornecedores:lista_fornecedores')
    template_name = 'fornecedores/confirm_delete.html'
    template_name_ajax = 'fornecedores/confirm_delete.html'  # Usado para modal também
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        # Exclui o objeto e responde conforme o tipo de requisição
        self.object = self.get_object()
        self.object.delete()

        if is_ajax(request):
            return JsonResponse({'success': True})
        return redirect(self.success_url)
