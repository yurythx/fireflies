import logging
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.http import JsonResponse, Http404
from django.db.models import Q

from .models import Cliente
from .forms import ClienteForm

logger = logging.getLogger(__name__)
PER_PAGE = 12


class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes/list-clientes.html'
    context_object_name = 'clientes'
    paginate_by = PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ClienteForm()
        return context


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/partials/form-cliente.html'
    success_url = reverse_lazy('clientes:list-clientes')

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Cliente cadastrado com sucesso!'})
        messages.success(self.request, 'Cliente cadastrado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        messages.error(self.request, 'Erro ao cadastrar cliente.')
        return super().form_invalid(form)

from django.http import JsonResponse
from django.views.generic import DetailView
from .models import Cliente

class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'cliente_detail.html'  # Você pode mudar isso caso queira usar uma template normal.

    # Quando usamos o DetailView com JSON, não precisamos renderizar um template
    # Então vamos sobrescrever o método get_context_data.
    def render_to_response(self, context, **response_kwargs):
        # Verifica se a requisição é uma requisição AJAX
        if self.request.is_ajax():
            cliente = self.get_object()  # Obtém o cliente com base no slug
            data = {
                'nome': cliente.nome,
                'email': cliente.email,
                'telefone': cliente.telefone,
                'endereco': cliente.endereco,
                'created_at': cliente.created_at,
            }
            return JsonResponse(data)
        else:
            # Se não for AJAX, exibe a página normalmente
            return super().render_to_response(context, **response_kwargs)

            
class ClienteUpdateView(UpdateView):
    model = Cliente
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    fields = ['nome', 'email', 'telefone', 'endereco']
    template_name = 'clientes/partials/form-cliente.html'  # O template que será usado para editar o cliente

    def get_success_url(self):
        return reverse_lazy('cliente_list')  # Redireciona para a lista de clientes após editar

    def form_valid(self, form):
        # Aqui você pode adicionar qualquer lógica antes de salvar, se necessário
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.object = self.get_object()
            form = self.get_form()
            return render(request, 'clientes/partials/form-cliente.html', {'form': form, 'cliente': self.object})
        return super().get(request, *args, **kwargs)


class ClienteDeleteView(DeleteView):
    model = Cliente
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('cliente_list')  # Redireciona para a lista de clientes após a exclusão

    def delete(self, request, *args, **kwargs):
        cliente = self.get_object()  # Obtém o cliente com base no slug
        cliente.delete()  # Exclui o cliente
        return JsonResponse({'success': True})  # Retorna sucesso em formato JSON


class SearchListView(ClienteListView):
    template_name = 'clientes/search-list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        if search:
            try:
                qs = qs.filter(
                    Q(nome__icontains=search) |
                    Q(email__icontains=search) |
                    Q(telefone__icontains=search)
                ).distinct()
            except Exception as e:
                logger.error(f"Erro ao filtrar clientes com o critério '{search}': {e}")
                qs = qs.none()
        return qs
