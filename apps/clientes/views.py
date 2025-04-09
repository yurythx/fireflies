from django.contrib import messages  # Para mensagens de feedback
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, DetailView
from django.views.generic import CreateView
from .forms import ClienteForm, EnderecoForm
from .models import Cliente, Endereco

PER_PAGE = 12


class ClienteListView(ListView):
    """Exibe a lista de clientes."""
    
    template_name = 'clientes/list-clientes.html'
    queryset = Cliente.objects.all()  # Lista todos os clientes
    paginate_by = PER_PAGE
    context_object_name = 'clientes'


class ClienteCreateView(CreateView):
    """Criação de um novo cliente com endereço"""
    
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/new-cliente.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['endereco_form'] = EnderecoForm()
        return context

    def form_valid(self, form):
        """Salva o cliente e o endereço"""
        cliente = form.save()
        endereco_form = EnderecoForm(self.request.POST)

        if endereco_form.is_valid():
            endereco = endereco_form.save(commit=False)
            endereco.cliente = cliente  # Vincula o endereço ao cliente
            endereco.save()
            messages.success(self.request, 'Cliente e endereço criados com sucesso!')
        else:
            messages.error(self.request, 'Erro ao salvar o endereço.')

        return redirect('clientes:cadastro_sucesso')


class ClienteDetailView(DetailView):
    """Exibe os detalhes do cliente."""
    
    model = Cliente
    template_name = 'clientes/cliente-details.html'
    context_object_name = 'cliente'

    def get_object(self):
        """Obtém o cliente usando o slug, ou gera um erro 404 se não encontrado."""
        slug = self.kwargs.get('slug')
        return get_object_or_404(Cliente, slug=slug)


class ClienteUpdateView(UpdateView):
    """Atualiza um cliente existente."""
    
    model = Cliente
    form_class = ClienteForm  # Usando o formulário correto
    template_name = 'clientes/update-cliente.html'

    def get_object(self, queryset=None):
        """Obtém o cliente com base no slug passado na URL"""
        return get_object_or_404(Cliente, slug=self.kwargs['slug'])

    def get_success_url(self):
        """Define a URL de redirecionamento após a edição bem-sucedida"""
        return reverse_lazy('clientes:cliente-details', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        """Adiciona uma mensagem de sucesso ao atualizar o cliente."""
        response = super().form_valid(form)
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return response


from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import Cliente, Estado, Cidade

def lista_clientes(request):
    estado_id = request.GET.get('estado')  # Obtém o ID do estado filtrado
    cidade_id = request.GET.get('cidade')  # Obtém o ID da cidade filtrada

    # Construir o filtro Q
    filtro = Q()

    if estado_id:
        filtro &= Q(endereco__estado_id=estado_id)  # Filtra os clientes pelo estado

    if cidade_id:
        filtro &= Q(endereco__cidade_id=cidade_id)  # Filtra os clientes pela cidade

    # Filtra os clientes com base nos parâmetros
    clientes = Cliente.objects.filter(filtro).select_related('endereco__cidade__estado')

    # Paginação: Mostra 10 clientes por página
    paginator = Paginator(clientes, 10)
    page = request.GET.get('page')
    clientes_paginados = paginator.get_page(page)

    # Obter todos os estados e cidades
    estados = Estado.objects.all()
    cidades = Cidade.objects.filter(estado_id=estado_id) if estado_id else Cidade.objects.none()

    return render(request, 'clientes/lista_clientes.html', {
        'clientes': clientes_paginados,
        'estados': estados,
        'cidades': cidades,
        'estado_id': estado_id,
        'cidade_id': cidade_id,
    })