from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.views import View
#from apps.enderecos.models import Cidade, Estado
from apps.enderecos.forms import EnderecoForm 
from .models import Cliente 
from .forms import ClienteForm  


# Função utilitária para detectar se a requisição é AJAX
def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


# View para listar todos os clientes
class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes/lista.html'  # Caminho do template que será renderizado
    context_object_name = 'clientes'
    paginate_by = 10  # Caso deseje paginar os resultados, pode configurar isso (opcional)

    def get_queryset(self):
        """
        Modifica o queryset para filtrar os clientes com base nos parâmetros de nome e CPF.
        """
        nome_busca = self.request.GET.get('nome', '')
        cpf_busca = self.request.GET.get('cpf', '')

        queryset = Cliente.objects.all()

        if nome_busca:
            queryset = queryset.filter(nome__icontains=nome_busca)
        if cpf_busca:
            queryset = queryset.filter(cpf__icontains=cpf_busca)

        return queryset


# Mixin reutilizável para requisições AJAX (modal)
class AjaxFormMixin:
    """
    Mixin que permite suporte AJAX para CreateView, UpdateView e DeleteView.
    Renderiza templates modais em requisições AJAX e responde com JSON.
    """
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


# View para criar um novo cliente
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form_modal.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'endereco_form' not in context:
            context['endereco_form'] = EnderecoForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        endereco_form = EnderecoForm(request.POST)

        if form.is_valid() and endereco_form.is_valid():
            with transaction.atomic():
                endereco = endereco_form.save()
                cliente = form.save(commit=False)
                cliente.endereco = endereco
                cliente.save()

            if is_ajax(request):
                return JsonResponse({
                    'success': True,
                    'message': 'Cliente criado com sucesso!',
                    'cliente_id': cliente.id
                })

            return self.form_valid(form)
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

            return render(request, self.template_name, {
                'form': form,
                'endereco_form': endereco_form
            })


# View para editar um cliente
class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form_modal.html'
    success_url = reverse_lazy('clientes:lista_clientes')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """
        Obtém o objeto cliente usando o 'slug' da URL.
        """
        cliente_slug = self.kwargs.get(self.slug_url_kwarg)
        return get_object_or_404(Cliente, slug=cliente_slug)

    def get_context_data(self, **kwargs):
        """
        Adiciona o formulário de endereço ao contexto.
        """
        context = super().get_context_data(**kwargs)
        cliente = self.get_object()
        context['endereco_form'] = EnderecoForm(instance=cliente.endereco)
        return context

    def post(self, request, *args, **kwargs):
        """
        Processa a atualização do cliente e do endereço via AJAX ou formulário tradicional.
        """
        self.object = self.get_object()
        cliente_form = self.get_form()
        endereco_form = EnderecoForm(request.POST, instance=self.object.endereco)

        if cliente_form.is_valid() and endereco_form.is_valid():
            with transaction.atomic():
                endereco = endereco_form.save()
                cliente = cliente_form.save(commit=False)
                cliente.endereco = endereco
                cliente.save()

            if is_ajax(request):
                return JsonResponse({
                    'success': True,
                    'message': 'Cliente atualizado com sucesso!',
                    'cliente_id': cliente.id
                })
            return super().form_valid(cliente_form)
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'errors': cliente_form.errors}, status=400)
            return render(request, self.template_name, {
                'form': cliente_form,
                'endereco_form': endereco_form
            })


# View para exibir os detalhes de um cliente
class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'clientes/detalhes_cliente_modal.html'  # Template para exibir no modal
    context_object_name = 'cliente'
    slug_field = 'slug'  # Campo que será usado para buscar o cliente
    slug_url_kwarg = 'slug'  # O parâmetro da URL que será usado para o slug

    def get_object(self):
        return Cliente.objects.get(slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        # Verifica se a requisição é AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            context = self.get_context_data()
            return render(request, self.template_name, context)  # Retorna o template parcial para o modal
        return super().get(request, *args, **kwargs)  # Caso contrário, renderiza a página normal

# View para excluir um cliente (com confirmação via modal AJAX)
class ClienteDeleteView(AjaxFormMixin, DeleteView):
    model = Cliente
    success_url = reverse_lazy('clientes:lista_clientes')
    template_name = 'clientes/confirm_delete.html'
    template_name_ajax = 'clientes/confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if is_ajax(request):
            return JsonResponse({'success': True})
        return redirect(self.success_url)
