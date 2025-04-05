from django.contrib import admin
from apps.articles.models import Tags, Category, Article

from django.utils.safestring import mark_safe


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'slug',
    )
    list_display_links = (
        'name',
    )
    search_fields = (
        'id', 'name', 'slug',
    )
    list_per_page = 10

    ordering = ('-id',)
    prepopulated_fields = {
        'slug': ('name',),
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'slug',
    )
    list_display_links = (
        'name',
    )
    search_fields = (
        'id', 'name', 'slug',
    )
    list_per_page = 10

    ordering = ('-id',)
    prepopulated_fields = {
        'slug': ('name',),
    }




@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    TinyMCE_fiedls = ('content',)
    list_display = (
        'id', 'title', 'is_published', 'created_by'
    )
    list_display_links = (
        'title',
    )
    search_fields = (
        'id', 'slug', 'title', 'excerpt', 'content',
    )
    list_per_page = (50)
    list_filter = (
        'category', 'is_published',
    )
    list_editable = ('is_published',)
    ordering = ('-id',)
    readonly_fields = (
        'created_at', 'updated_at', 'created_by', 'updated_by', 'link'
    )
    prepopulated_fields = {
        'slug': ('title', ),
    }
    autocomplete_fields = (
        'tags', 'category',
    )

    def link(self, obj):
        if not obj.pk:
            return 'empty'

        url_do_article = obj.get_absolute_url()

        return mark_safe(
            f'<a target="_blank" href="{url_do_article}">Ver Artigo</a>'
        )

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
        obj.save()