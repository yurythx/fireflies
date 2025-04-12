from django.db import models
from django.utils.text import slugify

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Gera o slug automaticamente se estiver vazio
        if not self.slug:
            self.slug = slugify(self.nome)

        # Verifica se o slug já existe e, se existir, cria um novo slug
        original_slug = self.slug
        counter = 1
        while Fornecedor.objects.filter(slug=self.slug).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1

        # Chama o método save do modelo para salvar os dados
        super().save(*args, **kwargs)