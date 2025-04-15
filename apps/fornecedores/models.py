from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import re
from django.db.utils import IntegrityError

# Modelo de Fornecedor
class Fornecedor(models.Model):
    """Modelo de Fornecedor."""

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=False, max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)  # CPF (opcional)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)  # CNPJ (opcional)
    data_fundacao = models.DateField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    endereco = models.OneToOneField('enderecos.Endereco', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nome

    def clean(self):
        """Validações personalizadas de CPF e CNPJ."""
        if self.cpf:
            if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', self.cpf):
                raise ValidationError({'cpf': "Formato de CPF inválido. Use XXX.XXX.XXX-XX"})
        
        if self.cnpj:
            if not re.match(r'^\d{2}\.\d{3}\.\d{3}/0001-\d{2}$', self.cnpj):
                raise ValidationError({'cnpj': "Formato de CNPJ inválido. Use XX.XXX.XXX/0001-XX"})

    def save(self, *args, **kwargs):
        """Criação ou atualização do slug automaticamente antes de salvar o fornecedor."""
        if not self.slug:
            self.slug = slugify(self.nome)

        # Garantir que o slug seja único, ignorando o próprio objeto no update
        original_slug = self.slug
        counter = 1
        while True:
            try:
                super().save(*args, **kwargs)  # Tenta salvar o objeto
                break  # Se não gerar erro, finaliza o loop
            except IntegrityError:  # Caso ocorra erro de unicidade (slug duplicado)
                # Se já houver um slug duplicado, incrementamos o número
                # Encontramos o maior número de sufixo usado e incrementamos
                max_suffix = Fornecedor.objects.filter(slug__startswith=original_slug).aggregate(models.Max('slug'))
                if max_suffix['slug__max']:
                    # Se já existir um sufixo, pegamos o maior número e incrementamos
                    suffix_number = int(max_suffix['slug__max'].split('-')[-1]) + 1
                else:
                    # Caso não haja sufixo, começamos pelo número 1
                    suffix_number = 1
                self.slug = f"{original_slug}-{suffix_number}"
        
        super().save(*args, **kwargs)
