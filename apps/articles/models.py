from django.db import models
from apps.utils.rands import slugify_new
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.urls import reverse


class ArticleManager(models.Manager):
    def get_published(self):
        return self.filter(is_published=True).order_by('-created_at')



class Tags(models.Model):
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    name = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True, max_length=100, default=None, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.name)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, max_length=200, default=None, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.name)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name



class Article(models.Model):
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    objects = ArticleManager()

    title = models.CharField(max_length=100, verbose_name = 'Titulo')
    slug = models.SlugField(
        unique=True, default='', null=False, blank=True, max_length=255
    )
    exerpt = models.CharField(max_length=100, verbose_name = 'Sumario')
    is_published = models.BooleanField(
        default=False,  verbose_name = 'Publicar ?',
        help_text='Marque essa opção para exibir a página.'
    )
    content = HTMLField(verbose_name = 'Conteúdo')
    cover = models.ImageField(
        upload_to='articles/%Y/%m', verbose_name = 'Imagem', blank=True, default=''
    )
    cover_in_post_content = models.BooleanField(
        default=True,
        help_text='Exibe a imagem de capa dentro do conteúdo do post'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name = 'Criado em')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, verbose_name = 'Criado por', null=True,
        related_name='article_created_by',
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name = 'Modificado em ')
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name = 'Modificado por',
        related_name='article_updated_by',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, default=None
    )
    tags = models.ManyToManyField(Tags, blank=True, default='')

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        if not self.is_published:
            return reverse('articles:index_articles')

        return reverse('articles:article', args=(self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.title)

        current_cover_name = str(self.cover.name)
        super_save = super().save(*args, **kwargs)
        cover_changed = False

        if self.cover:
            cover_changed = current_cover_name != self.cover.name

        #if cover_changed:
        #    resize_image(self.cover, 900, optimize=True, quality=70)

        def __str__(self):
            return self.title 
        
        return super_save