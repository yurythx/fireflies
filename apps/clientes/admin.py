from django.contrib import admin
from .models import Cliente

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

    )
    list_display_links = ('nome', 'email')  # Campos clicáveis para edição
    search_fields = ('nome', 'cpf', 'email')  # Permitir pesquisa por nome, CPF ou email
    date_hierarchy = 'data_nascimento'  # Permitir visualização hierárquica por data de nascimento
    list_editable = ('telefone', 'data_nascimento')  # Campos que podem ser editados diretamente
    ordering = ('-data_cadastro',)  # Ordenação dos clientes do mais recente para o mais antigo
    actions = ['marcar_como_inativo']  # Ações personalizadas

    # Método para marcar clientes como inativos
    def marcar_como_inativo(self, request, queryset):
        queryset.update(estado="Inativo")  # Atualiza o estado do cliente para 'Inativo'
        self.message_user(request, "Cliente(s) marcado(s) como inativo(s).")

    marcar_como_inativo.short_description = "Marcar como Inativo"


admin.site.register(Cliente, ClienteAdmin)
