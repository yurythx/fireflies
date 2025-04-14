from django.contrib import admin
from .models import Estado, Cidade, Endereco


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')
    ordering = ('nome',)


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'estado')
    list_filter = ('estado',)
    search_fields = ('nome',)
    ordering = ('estado__nome', 'nome')


class EnderecoInline(admin.StackedInline):
    model = Endereco
    extra = 0
    show_change_link = True


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('rua', 'numero', 'bairro', 'cidade', 'estado', 'cep', 'criado_em')
    list_filter = ('estado', 'cidade')
    search_fields = ('rua', 'bairro', 'cidade__nome', 'estado__nome', 'cep')
    ordering = ('-criado_em',)

    fieldsets = (
        ('Dados do Endereço', {
            'fields': ('rua', 'numero', 'complemento', 'bairro')
        }),
        ('Localização', {
            'fields': ('estado', 'cidade', 'cep')
        }),
        ('Metadados', {
            'fields': ('criado_em',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('criado_em',)
