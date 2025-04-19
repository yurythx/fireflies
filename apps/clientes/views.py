# Importações padrão do Django para views genéricas e manipulação de requisições
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
import logging

# Importa o modelo e os formulários utilizados
from .models import Cliente
from .forms import ClienteForm
from apps.enderecos.forms import EnderecoForm


# Função auxiliar para detectar requisições AJAX modernas
def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


# Mixin reutilizável para views de listagem que precisam retornar HTML parcial via AJAX
class AjaxListMixin:
    partial_template_name = None  # Template usado para renderização AJAX

    def render_to_response(self, context, **response_kwargs):
        if is_ajax(self.request) and self.partial_template_name:
            return render(self.request, self.partial_template_name, context)
        return super().render_to_response(context, **response_kwargs)


# View de listagem de clientes com filtro e suporte AJAX
class ClienteListView(AjaxListMixin, ListView):
    model = Cliente
    template_name = 'clientes/lista_clientes.html'
    partial_template_name = 'clientes/_lista_clientes.html'
    context_object_name = 'clientes'

    def get_queryset(self):
        # Obtém filtros da requisição
        nome_busca = self.request.GET.get('nome', '')
        cpf_busca = self.request.GET.get('cpf', '')

        queryset = Cliente.objects.all()
        # Aplica filtros se fornecidos
        if nome_busca:
            queryset = queryset.filter(nome__icontains=nome_busca)
        if cpf_busca:
            queryset = queryset.filter(cpf__icontains=cpf_busca)
        return queryset


# Mixin que facilita manipulação de formulários via AJAX
class AjaxFormMixin:
    template_name_ajax = None  # Template para renderização AJAX de formulários

    def form_invalid(self, form):
        if is_ajax(self.request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        # Em caso de DeleteView, executa a exclusão diretamente
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
            return render(request, self.template_name_ajax or self.template_name, context)
        return super().get(request, *args, **kwargs)


# View para criação de clientes com endereço
class ClienteCreateView(AjaxFormMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form_clientes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o formulário de endereço ao contexto
        context['endereco_form'] = kwargs.get('endereco_form') or EnderecoForm()
        return context

    def get_endereco_form(self):
        return EnderecoForm(self.request.POST)

    def handle_endereco_form_errors(self, endereco_form, form_errors=None):
        return JsonResponse({
            'success': False,
            'errors': form_errors or {},
            'endereco_errors': endereco_form.errors
        }, status=400)

    @transaction.atomic  # Garante atomicidade entre cliente e endereço
    def form_valid(self, form):
        endereco_form = self.get_endereco_form()

        if not endereco_form.is_valid():
            return self.handle_endereco_form_errors(endereco_form)

        endereco = endereco_form.save()
        cliente = form.save(commit=False)
        cliente.endereco = endereco
        cliente.save()

        if is_ajax(self.request):
            return JsonResponse({'success': True, 'message': 'Cliente criado com sucesso!'})
        messages.success(self.request, 'Cliente criado com sucesso!')
        return redirect('clientes:lista_clientes')

    def form_invalid(self, form):
        endereco_form = self.get_endereco_form()
        return self.handle_endereco_form_errors(endereco_form, form.errors)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if is_ajax(request):
            return self.form_valid(form) if form.is_valid() else self.form_invalid(form)
        return super().post(request, *args, **kwargs)


# View para atualização de clientes
class ClienteUpdateView(AjaxFormMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form_clientes.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.get_object()
        context['endereco_form'] = kwargs.get('endereco_form') or EnderecoForm(instance=cliente.endereco)
        return context

    def get_endereco_form(self, instance):
        return EnderecoForm(self.request.POST, instance=instance)

    def handle_endereco_form_errors(self, endereco_form, form_errors=None):
        return JsonResponse({
            'success': False,
            'errors': form_errors or {},
            'endereco_errors': endereco_form.errors
        }, status=400)

    @transaction.atomic
    def form_valid(self, form):
        cliente = form.save(commit=False)
        endereco_form = self.get_endereco_form(cliente.endereco)

        if not endereco_form.is_valid():
            return self.handle_endereco_form_errors(endereco_form)

        endereco = endereco_form.save()
        cliente.endereco = endereco
        cliente.save()

        if is_ajax(self.request):
            return JsonResponse({'success': True, 'message': 'Cliente atualizado com sucesso!'})
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return redirect('clientes:lista_clientes')

    def form_invalid(self, form):
        cliente = self.get_object()
        endereco_form = self.get_endereco_form(cliente.endereco)
        return self.handle_endereco_form_errors(endereco_form, form.errors)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if is_ajax(request):
            return self.form_valid(form) if form.is_valid() else self.form_invalid(form)
        return super().post(request, *args, **kwargs)


# View para exibir detalhes do cliente (usado para modal)
class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'clientes/detalhes_cliente_modal.html'
    context_object_name = 'cliente'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        return get_object_or_404(Cliente, slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = self.get_object()
            context = self.get_context_data()
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)


# View para exclusão de clientes
# Inicializando o logger
logger = logging.getLogger(__name__)

class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'clientes/confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('clientes:lista_clientes')

    def get_object(self, queryset=None):
        # Obter o cliente com base no slug
        slug = self.kwargs.get('slug')
        logger.debug(f"Slug recebido: {slug}")
        cliente = get_object_or_404(Cliente, slug=slug)
        return cliente

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.debug(f"Contexto para renderização: {context}")
        return context

    def get(self, request, *args, **kwargs):
        # Chamando get_object e get_context_data para processar o GET
        self.object = self.get_object()
        context = self.get_context_data()
        logger.debug(f"Requisição GET para excluir cliente {self.object.nome}")

        if is_ajax(request):
            # Se for uma requisição AJAX, renderiza o template diretamente
            return render(request, self.template_name, context)
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Chamando get_object novamente para garantir que estamos lidando com o objeto correto
        self.object = self.get_object()
        nome = self.object.nome
        logger.debug(f"Iniciando exclusão do cliente: {nome}")

        try:
            self.object.delete()
            logger.debug(f"Cliente {nome} excluído com sucesso")
            success_message = f'Cliente "{nome}" excluído com sucesso!'
            
            if is_ajax(request):
                return JsonResponse({'success': True, 'message': success_message})

            # Caso contrário, exibe a mensagem de sucesso e redireciona
            messages.success(request, success_message)
            return redirect(self.success_url)
        
        except Exception as e:
            logger.error(f"Erro ao excluir cliente {nome}: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Erro ao excluir cliente.'})