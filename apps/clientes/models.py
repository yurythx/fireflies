from django.db import models
from apps.enderecos.forms import EnderecoForm
from django.utils.text import slugify  # Importando a função slugify


# Modelo de Cliente
class Cliente(models.Model):
    """Modelo de Cliente.""" 

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=False, max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    endereco = models.OneToOneField('enderecos.Endereco', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
     """Criação ou atualização do slug automaticamente antes de salvar o cliente."""
     if not self.slug:
         self.slug = slugify(self.nome)
     
     # Garantir que o slug seja único
     original_slug = self.slug
     counter = 1
     while Cliente.objects.filter(slug=self.slug).exists():
         self.slug = f"{original_slug}-{counter}"
         counter += 1
     
     super().save(*args, **kwargs)



