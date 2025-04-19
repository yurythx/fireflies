from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator
from tinymce.models import HTMLField
import uuid

from apps.utils.rands import slugify_new  # Caso você ainda deseje usar a função slugify_new

class ArticleManager(models.Manager):
    """Gerenciador de artigos filtrando apenas os publicados."""

    def get_published(self):
        return self.filter(is_published=True).order_by('-created_at')


class Tags(models.Model):
    """Modelo de Tag para classificar artigos."""

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(
        unique=True,
        max_length=100,
        blank=True,
        null=True,
        default=None,
        allow_unicode=True
    )

    def save(self, *args, **kwargs):
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

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(
        unique=True,
        max_length=200,
        blank=True,
        null=True,
        default=None,
        allow_unicode=True
    )

    def save(self, *args, **kwargs):
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
        ordering = ['-created_at']

    objects = ArticleManager()

    title = models.CharField(max_length=100, verbose_name='Título')
    slug = models.SlugField(
        unique=True,
        blank=True,  # Pode ser em branco até que o slug seja gerado
        null=False,
        max_length=255,
        allow_unicode=True
    )
    excerpt = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100, message=_("O resumo não pode passar de 100 caracteres."))],
        verbose_name='Resumo'
    )
    is_published = models.BooleanField(
        default=False,
        help_text=_('Marque essa opção para exibir a página.'),
        verbose_name='Marque para publicar'
    )
    content = HTMLField()
    cover = models.ImageField(upload_to='articles/%Y/%m', blank=True, default='')
    imagem_article = models.ImageField(
        upload_to='post_img/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Imagem'
    )
    cover_in_post_content = models.BooleanField(
        default=True,
        help_text=_('Exibe a imagem de capa dentro do conteúdo do post')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles_created'
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles_updated'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        verbose_name='Categoria'
    )
    tags = models.ManyToManyField(
        Tags,
        blank=True,
        verbose_name='Tags'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if not self.is_published:
            return reverse('articles:index_articles')
        return reverse('articles:article-details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:  # Se o slug não estiver definido, gerar automaticamente
            self.slug = self.generate_slug_from_title()

        # Garantir que o slug seja único
        while Article.objects.filter(slug=self.slug).exists():
            self.slug = self.generate_slug_from_title() + '-' + str(uuid.uuid4())[:8]

        super().save(*args, **kwargs)

    def generate_slug_from_title(self):
        """
        Gera um slug a partir do título do artigo.
        """
        return slugify(self.title)


class Comment(models.Model):
    """Modelo de comentário associado ao artigo."""

    article = models.ForeignKey(
        'Article',  # Referência para o modelo Article
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author_name = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100, message=_("O nome do autor não pode ultrapassar 100 caracteres."))],
        verbose_name='Nome do autor'
    )
    text = models.TextField(
        validators=[MaxLengthValidator(2000, message=_("O comentário não pode ultrapassar 2000 caracteres."))],
        verbose_name='Comentário'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de atualização')
    is_approved = models.BooleanField(default=False, verbose_name='Aprovado')
    is_spam = models.BooleanField(default=False, verbose_name='É spam?')  # Marca como spam
    parent_comment = models.ForeignKey(
        'self',  # Relacionamento com o próprio modelo
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='Comentário pai'  # Permite a hierarquia de respostas
    )

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['created_at']  # Ordena os comentários pela data de criação

    def __str__(self):
        return f'Comentário de {self.author_name}'

    def approve(self):
        """Método para aprovar o comentário."""
        self.is_approved = True
        self.save()

    def disapprove(self):
        """Método para desaprovar o comentário."""
        self.is_approved = False
        self.save()

    def mark_as_spam(self):
        """Método para marcar o comentário como spam."""
        self.is_spam = True
        self.save()

    def unmark_as_spam(self):
        """Método para desmarcar o comentário como spam."""
        self.is_spam = False
        self.save()