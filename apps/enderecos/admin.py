from django.contrib import admin
from .models import Estado, Cidade, Endereco

# Admin para o modelo Estado
class EstadoAdmin(admin.ModelAdmin):
    # Exibição de campos na lista
    list_display = ('nome', 'sigla')

    # Campos que serão buscáveis
    search_fields = ('nome', 'sigla')

    # Filtros por nome e sigla
    list_filter = ('nome', 'sigla')

# Admin para o modelo Cidade
class CidadeAdmin(admin.ModelAdmin):
    # Exibição de campos na lista
    list_display = ('nome', 'estado')

    # Filtros para as cidades por estado
    list_filter = ('estado',)

    # Campos que serão buscáveis
    search_fields = ('nome',)

# Admin para o modelo Endereco
class EnderecoAdmin(admin.ModelAdmin):
    # Exibição de campos na lista
    list_display = ('rua', 'numero', 'bairro', 'estado', 'cidade', 'cep',)

    # Filtros por cidade e estado
    list_filter = ('estado', 'cidade')

    # Campos que serão buscáveis
    search_fields = ('rua', 'bairro', 'cep')

    # Exibição de detalhes ao clicar no item da lista
    fieldsets = (
        (None, {
            'fields': ('rua', 'numero', 'complemento', 'bairro', 'estado', 'cidade', 'cep')
        }),
    )

    # Remover 'criado_em' de fieldsets pois é um campo não editável
    # O Django já irá gerenciar esse campo automaticamente

# Registrar os modelos no Django Admin
admin.site.register(Estado, EstadoAdmin)
admin.site.register(Cidade, CidadeAdmin)
admin.site.register(Endereco, EnderecoAdmin)
