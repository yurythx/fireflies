from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from .models import Fornecedor
from .forms import FornecedorForm
from apps.enderecos.forms import EnderecoForm


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


class FornecedorListView(ListView):
    model = Fornecedor
    template_name = 'fornecedores/lista_fornecedores.html'
    context_object_name = 'fornecedores'

    def render_to_response(self, context, **response_kwargs):
        if is_ajax(self.request):
            return render(self.request, 'fornecedores/_lista_fornecedores.html', context)
        return super().render_to_response(context, **response_kwargs)

    def get_queryset(self):
        """
        Modifica o queryset para filtrar os fornecedores com base nos parâmetros de nome e CNPJ.
        """
        nome_busca = self.request.GET.get('nome', '')
        cnpj_busca = self.request.GET.get('cnpj', '')

        queryset = Fornecedor.objects.all()

        if nome_busca:
            queryset = queryset.filter(nome__icontains=nome_busca)
        if cnpj_busca:
            queryset = queryset.filter(cnpj__icontains=cnpj_busca)

        return queryset


# Mixin reutilizável para requisições AJAX (modal)
class AjaxFormMixin:
    template_name_ajax = None  # Template alternativo a ser usado quando a requisição for AJAX

    def form_invalid(self, form):
        if is_ajax(self.request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        if isinstance(self, DeleteView):
            return self.delete(self.request)

        self.object = form.save()

        if is_ajax(self.request):
            return JsonResponse({'success': True})

        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            try:
                self.object = self.get_object()
            except AttributeError:
                self.object = None

            context = self.get_context_data()
            return render(request, self.template_name_ajax, context)

        return super().get(request, *args, **kwargs)


# View para criar um novo fornecedor
class FornecedorCreateView(CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'fornecedores/form_fornecedor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['endereco_form'] = kwargs.get('endereco_form') or EnderecoForm()
        return context

    def form_invalid(self, form):
        # Processa erro do formulário principal + formulário de endereço
        endereco_form = EnderecoForm(self.request.POST)
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'endereco_errors': endereco_form.errors if not endereco_form.is_valid() else {}
        }, status=400)

    def form_valid(self, form):
        fornecedor = form.save()
        endereco_form = EnderecoForm(self.request.POST)

        if endereco_form.is_valid():
            endereco = endereco_form.save()
            fornecedor.endereco = endereco
            fornecedor.save()
            return JsonResponse({'success': True, 'message': 'Fornecedor criado com sucesso!'})
        else:
            return JsonResponse({
                'success': False,
                'errors': {},
                'endereco_errors': endereco_form.errors
            }, status=400)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

# View para editar um fornecedor
class FornecedorUpdateView(UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'fornecedores/form_fornecedor.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fornecedor = self.get_object()
        # Popula o formulário de endereço com o existente
        context['endereco_form'] = kwargs.get('endereco_form') or EnderecoForm(instance=fornecedor.endereco)
        return context

    def form_invalid(self, form):
        fornecedor = self.get_object()
        endereco_form = EnderecoForm(self.request.POST, instance=fornecedor.endereco)

        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'endereco_errors': endereco_form.errors if not endereco_form.is_valid() else {}
        }, status=400)

    def form_valid(self, form):
        fornecedor = form.save()
        endereco_form = EnderecoForm(self.request.POST, instance=fornecedor.endereco)

        if endereco_form.is_valid():
            endereco_form.save()
            return JsonResponse({'success': True, 'message': 'Fornecedor atualizado com sucesso!'})
        else:
            return JsonResponse({
                'success': False,
                'errors': {},
                'endereco_errors': endereco_form.errors
            }, status=400)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        return super().post(request, *args, **kwargs)


# View para exibir os detalhes de um fornecedor
class FornecedorDetailView(DetailView):
    model = Fornecedor
    template_name = 'fornecedores/detalhes_fornecedor_modal.html'
    context_object_name = 'fornecedor'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        return Fornecedor.objects.get(slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            context = self.get_context_data()
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)

class FornecedorDeleteView(DeleteView):
    model = Fornecedor
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'fornecedores/confirm_delete.html'
    success_url = reverse_lazy('fornecedores:lista_fornecedores')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Fornecedor excluído com sucesso!'})
        
        return super().delete(request, *args, **kwargs)