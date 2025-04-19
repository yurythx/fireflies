from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from unidecode import unidecode
import re

class Cliente(models.Model):
    """Modelo de Cliente."""

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=False, max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)  # CPF (opcional)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)  # CNPJ (opcional)
    data_nascimento = models.DateField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    endereco = models.OneToOneField('enderecos.Endereco', on_delete=models.CASCADE, null=True, blank=True)
  

    def __str__(self):
        return self.nome

    def clean(self):
        """Validações e formatações personalizadas de CPF e CNPJ."""

        if self.cpf:
            cpf_numeros = re.sub(r'\D', '', self.cpf)

            if len(cpf_numeros) != 11:
                raise ValidationError({'cpf': "CPF deve conter 11 dígitos."})

            # Formata como XXX.XXX.XXX-XX
            self.cpf = f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
        
        if self.cnpj:
            cnpj_numeros = re.sub(r'\D', '', self.cnpj)

            if len(cnpj_numeros) != 14:
                raise ValidationError({'cnpj': "CNPJ deve conter 14 dígitos."})

            # Formata como XX.XXX.XXX/0001-XX
            self.cnpj = f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}.{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:]}"
        
        # Pelo menos um dos dois deve ser informado
        if not self.cpf and not self.cnpj:
            raise ValidationError("Informe pelo menos o CPF ou o CNPJ.")

    def save(self, *args, **kwargs):
        """Geração automática e segura de slug único."""

        if not self.slug:
            base_slug = slugify(unidecode(self.nome))
            slug = base_slug
            counter = 1
            while Cliente.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        self.full_clean()  # Garante que clean() será chamado
        super().save(*args, **kwargs)
