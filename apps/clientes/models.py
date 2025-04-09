from django.db import models


# Modelo para Estados
class Estado(models.Model):
    """Modelo de Estado.""" 
    nome = models.CharField(max_length=100)
    uf = models.CharField(max_length=2, unique=True)  # Sigla do estado, por exemplo, 'SP'

    def __str__(self):
        return self.nome


# Modelo para Cidades
class Cidade(models.Model):
    """Modelo de Cidade.""" 
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, related_name='cidades', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nome} - {self.estado.uf}'


# Modelo para Endereço
class Endereco(models.Model):
    """Modelo de Endereço.""" 
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return f'{self.rua}, {self.numero} - {self.bairro}, {self.cidade.nome}, {self.estado.uf}'


# Modelo de Cliente
class Cliente(models.Model):
    """Modelo de Cliente.""" 
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    endereco = models.OneToOneField(Endereco, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome