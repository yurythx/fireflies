from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from unidecode import unidecode
from django.utils import timezone

class Produto(models.Model):
    """Modelo representando um produto com validações completas e funcionalidades adicionais."""

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['categoria']),
        ]

    STATUS_DISPONIVEL = 'disponivel'
    STATUS_INDISPONIVEL = 'indisponivel'
    STATUS_PROMOCAO = 'promocao'

    STATUS_CHOICES = [
        (STATUS_DISPONIVEL, 'Disponível'),
        (STATUS_INDISPONIVEL, 'Indisponível'),
        (STATUS_PROMOCAO, 'Promoção'),
    ]

    nome = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=20, unique=True, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=False, max_length=255)

    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)

    estoque = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)

    # Novos campos
    peso = models.PositiveIntegerField(default=0, help_text="Peso do produto em gramas.")
    largura = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Largura do produto em centímetros.")
    altura = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Altura do produto em centímetros.")
    profundidade = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Profundidade do produto em centímetros.")
    marca = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DISPONIVEL)
    status_message = models.CharField(max_length=255, blank=True, null=True)

    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    visivel = models.BooleanField(default=True)

    promocao_inicio = models.DateTimeField(null=True, blank=True)
    promocao_fim = models.DateTimeField(null=True, blank=True)

    produtos_relacionados = models.ManyToManyField('self', blank=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    @property
    def em_promocao(self):
        now = timezone.now()
        return (
            self.promocao_inicio and self.promocao_fim and
            self.promocao_inicio <= now <= self.promocao_fim
        )

    def _validar_imagem(self):
        if self.imagem:
            max_size_mb = 5
            if self.imagem.size > max_size_mb * 1024 * 1024:
                raise ValidationError({'imagem': f"A imagem não pode ultrapassar {max_size_mb}MB."})

            valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
            ext = self.imagem.name.lower().split('.')[-1]
            if self.imagem.file.content_type not in valid_mime_types or ext not in ['jpg', 'jpeg', 'png', 'gif']:
                raise ValidationError({'imagem': "A imagem deve estar nos formatos: JPEG, PNG ou GIF."})

    def _validar_promocao(self):
        if self.promocao_inicio and self.promocao_fim:
            if self.promocao_inicio >= self.promocao_fim:
                raise ValidationError({'promocao_fim': "A data de término da promoção deve ser posterior à de início."})

    def clean(self):
        if self.preco < 0:
            raise ValidationError({'preco': "O preço não pode ser negativo."})

        self._validar_imagem()
        self._validar_promocao()

        if self.status == self.STATUS_INDISPONIVEL and not self.status_message:
            self.status_message = "Produto fora de estoque."

    def save(self, *args, **kwargs):
        # Slug automático
        if not self.slug:
            base_slug = slugify(unidecode(self.nome))
            slug = base_slug
            counter = 1
            while Produto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Status automático baseado no estoque e promoção
        if self.estoque == 0:
            self.status = self.STATUS_INDISPONIVEL
        elif self.em_promocao:
            self.status = self.STATUS_PROMOCAO
        else:
            self.status = self.STATUS_DISPONIVEL

        self.full_clean()
        super().save(*args, **kwargs)

    def atualizar_estoque(self, quantidade):
        """Método para atualizar o estoque do produto."""
        novo_estoque = self.estoque + quantidade
        if novo_estoque < 0:
            raise ValidationError("O estoque não pode ser negativo.")
        self.estoque = novo_estoque
        self.save()

class ImagemProduto(models.Model):
    """Múltiplas imagens para cada produto."""
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/galeria/')
    legenda = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Imagem de {self.produto.nome}"

class Categoria(models.Model):
    """Modelo representando a categoria de um produto."""
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome