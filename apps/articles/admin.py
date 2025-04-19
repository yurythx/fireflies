from django.contrib import admin
from tinymce.widgets import TinyMCE
from django.db import models
from .models import Article, Tags, Category, Comment

class ArticleAdmin(admin.ModelAdmin):
    """Admin para o modelo de Artigo com TinyMCE no campo 'content'."""

    # Definindo as colunas na lista de artigos
    list_display = ('title', 'category', 'created_at', 'is_published')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'content', 'category__name')

    # Usando o TinyMCE no campo 'content'
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }

class CommentAdmin(admin.ModelAdmin):
    """Admin para o modelo de Comentário."""
    list_display = ('author_name', 'article', 'created_at', 'is_approved', 'is_spam')
    list_filter = ('is_approved', 'is_spam', 'created_at')  # Filtrando pelos campos corretos
    search_fields = ('author_name', 'text', 'article__title')  # Adicionando pesquisa nos campos de interesse

    # Se você quiser adicionar ações personalizadas, como aprovar ou marcar como spam, você pode fazer:
    actions = ['approve_comments', 'disapprove_comments', 'mark_as_spam', 'unmark_as_spam']

    def approve_comments(self, request, queryset):
        """Ação para aprovar os comentários selecionados."""
        queryset.update(is_approved=True)

    def disapprove_comments(self, request, queryset):
        """Ação para desaprovar os comentários selecionados."""
        queryset.update(is_approved=False)

    def mark_as_spam(self, request, queryset):
        """Ação para marcar os comentários selecionados como spam."""
        queryset.update(is_spam=True)

    def unmark_as_spam(self, request, queryset):
        """Ação para desmarcar os comentários selecionados como spam."""
        queryset.update(is_spam=False)

    approve_comments.short_description = 'Aprovar comentários'
    disapprove_comments.short_description = 'Desaprovar comentários'
    mark_as_spam.short_description = 'Marcar como spam'
    unmark_as_spam.short_description = 'Desmarcar como spam'



class TagsAdmin(admin.ModelAdmin):
    """Admin para o modelo de Tags."""
    list_display = ('name', 'slug')
    search_fields = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    """Admin para o modelo de Categoria."""
    list_display = ('name', 'slug')
    search_fields = ('name',)

# Registrando os modelos no Django Admin
admin.site.register(Article, ArticleAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)