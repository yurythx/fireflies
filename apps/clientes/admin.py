from django.contrib import admin
from .models import Estado, Cidade, Endereco, Cliente

# Registro do modelo Estado
class EstadoAdmin(admin.ModelAdmin):
    """Configuração do modelo Estado no Django Admin.""" 
    list_display = ('nome', 'uf')  # Campos a serem exibidos na lista
    search_fields = ('nome', 'uf')  # Permitir pesquisa por nome e sigla
    ordering = ('nome',)  # Ordenar por nome

admin.site.register(Estado, EstadoAdmin)


# Registro do modelo Cidade
class CidadeAdmin(admin.ModelAdmin):
    """Configuração do modelo Cidade no Django Admin.""" 
    list_display = ('nome', 'estado')  # Campos a serem exibidos na lista
    search_fields = ('nome',)  # Permitir pesquisa por nome da cidade
    list_filter = ('estado',)  # Permitir filtrar por estado
    ordering = ('nome',)  # Ordenar por nome da cidade

admin.site.register(Cidade, CidadeAdmin)


# Registro do modelo Endereco
class EnderecoAdmin(admin.ModelAdmin):
    """Configuração do modelo Endereco no Django Admin.""" 
    list_display = ('rua', 'numero', 'bairro', 'cidade', 'estado', 'cep')  # Campos a serem exibidos na lista
    search_fields = ('rua', 'bairro', 'cep')  # Permitir pesquisa por rua, bairro e CEP
    list_filter = ('cidade', 'estado')  # Permitir filtrar por cidade e estado
    ordering = ('bairro',)  # Ordenar por bairro

admin.site.register(Endereco, EnderecoAdmin)


# Registro do modelo Cliente
class ClienteAdmin(admin.ModelAdmin):
    """Configuração personalizada para o modelo Cliente no admin.""" 
    list_display = (
        'nome', 
        'email', 
        'telefone', 
        'cpf', 
        'data_nascimento', 
        'data_cadastro', 
        'get_estado', 
        'get_cidade'
    )
    list_display_links = ('nome', 'email')  # Campos clicáveis para edição
    search_fields = ('nome', 'cpf', 'email')  # Permitir pesquisa por nome, CPF ou email
    date_hierarchy = 'data_nascimento'  # Permitir visualização hierárquica por data de nascimento
    list_filter = ('endereco__estado', 'endereco__cidade', 'data_cadastro')  # Filtros laterais
    list_editable = ('telefone', 'data_nascimento')  # Campos que podem ser editados diretamente
    ordering = ('-data_cadastro',)  # Ordenação dos clientes do mais recente para o mais antigo
    actions = ['marcar_como_inativo']  # Ações personalizadas

    # Método para marcar clientes como inativos
    def marcar_como_inativo(self, request, queryset):
        queryset.update(estado="Inativo")  # Atualiza o estado do cliente para 'Inativo'
        self.message_user(request, "Cliente(s) marcado(s) como inativo(s).")

    marcar_como_inativo.short_description = "Marcar como Inativo"

    # Métodos personalizados para acessar o estado e a cidade do cliente
    def get_estado(self, obj):
        return obj.endereco.estado.uf if obj.endereco and obj.endereco.estado else 'Não Informado'
    get_estado.short_description = 'Estado'

    def get_cidade(self, obj):
        return obj.endereco.cidade.nome if obj.endereco and obj.endereco.cidade else 'Não Informado'
    get_cidade.short_description = 'Cidade'

admin.site.register(Cliente, ClienteAdmin)
