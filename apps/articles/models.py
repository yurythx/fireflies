from django.db import models
from apps.utils.rands import slugify_new
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator


class ArticleManager(models.Manager):
    """Gerenciador de artigos filtrando apenas os publicados."""
    
    def get_published(self):
        """Retorna artigos publicados, ordenados por data de criação."""
        return self.filter(is_published=True).order_by('-created_at')


class Tags(models.Model):
    """Modelo de Tag para classificar artigos."""
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True, default=None)

    def save(self, *args, **kwargs):
        """Salva a tag, gerando um slug se necessário."""
        if not self.slug:
            self.slug = slugify_new(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Modelo de Categoria para organizar os artigos."""
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=200, blank=True, null=True, default=None)

    def save(self, *args, **kwargs):
        """Salva a categoria, gerando um slug se necessário."""
        if not self.slug:
            self.slug = slugify_new(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    """Modelo de Artigo, que contém o título, conteúdo, categorias e tags."""
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    objects = ArticleManager()

    title = models.CharField(max_length=100, verbose_name='Titulo')
    slug = models.SlugField(unique=True, blank=True, null=False, max_length=255)
    excerpt = models.CharField(max_length=100, verbose_name='Resumo')
    is_published = models.BooleanField(default=False, help_text=_('Marque essa opção para exibir a página.'),verbose_name='Marque para publicar')
    content = HTMLField()
    cover = models.ImageField(upload_to='articles/%Y/%m', blank=True, default='')
    imagem_article = models.ImageField(upload_to='post_img/%Y/%m/%d', blank=True, null=True, verbose_name='Imagem')
    cover_in_post_content = models.BooleanField(default=True, help_text=_('Exibe a imagem de capa dentro do conteúdo do post'))
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='article_created_by',verbose_name='Criado Por')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='article_updated_by', verbose_name='Alterado Por')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, default=None,verbose_name='Categoria')
    tags = models.ManyToManyField(Tags, blank=True, default='', verbose_name='Tag')

    class Meta:
        ordering = ['-created_at']  # Ordena todos os artigos pela data de criação, do mais recente para o mais antigo
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Retorna a URL do artigo, levando em consideração se ele está publicado ou não."""
        if not self.is_published:
            return reverse('articles:index_articles')
        return reverse('articles:article-details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """Salva o artigo, gerando o slug e tratando alterações na capa."""
        if not self.slug:
            self.slug = slugify_new(self.title)

        current_cover_name = str(self.cover.name)
        super().save(*args, **kwargs)  # Salvar o artigo
        
        if self.cover and current_cover_name != str(self.cover.name):
            # Se a capa foi alterada, você pode adicionar um processo de redimensionamento aqui
            pass

        return super().save(*args, **kwargs)


class Comment(models.Model):
    """Modelo de comentário associado ao artigo."""
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author_name}'