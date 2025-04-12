from django.contrib import admin
from .models import Cliente
from apps.enderecos.models import Endereco
from apps.enderecos.forms import EnderecoForm

class ClienteAdmin(admin.ModelAdmin):
    # Exibir campos no list display
    list_display = ('nome', 'email', 'telefone', 'cpf', 'data_nascimento', 'data_cadastro', 'endereco')
    
    # Campos de filtro
    list_filter = ('data_nascimento', 'data_cadastro')

    # Adicionar busca por nome, e-mail e CPF
    search_fields = ('nome', 'email', 'cpf')

    # Campos que são editáveis diretamente na lista
    list_editable = ('telefone',)

    # Exibição de detalhes ao clicar em um item da lista
    fieldsets = (
        (None, {
            'fields': ('nome', 'email', 'telefone', 'cpf', 'data_nascimento', 'endereco')
        }),
        ('Datas', {
            'fields': ('data_cadastro',)
        }),
    )

    # Formulário customizado para Endereço (se necessário)
    form = EnderecoForm

    # Permite exibir o slug, mas de forma editável ou apenas leitura
    readonly_fields = ('slug', 'data_cadastro')

    # Salvar com a lógica customizada, se necessário
    def save_model(self, request, obj, form, change):
        """Personalize a criação ou atualização no admin"""
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Customizar consulta para exibir apenas clientes ativos, se necessário"""
        return super().get_queryset(request)


# Registrar o modelo Cliente no Admin
admin.site.register(Cliente, ClienteAdmin)
