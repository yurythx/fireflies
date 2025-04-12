from django.db import models



class Estado(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=2)  # Ex: SP, RJ, MG

    def __str__(self):
        return f"{self.nome} ({self.sigla})"



class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='cidades')

    def __str__(self):
        return self.nome

class Endereco(models.Model):
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)  # Relacionando com a cidade
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)  # Relacionando com o estado
    cep = models.CharField(max_length=9)  # Ex: 12345-678
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cidade.nome}/{self.estado.sigla}"

    def get_cidades_por_estado(self):
        # Método auxiliar para obter cidades relacionadas ao estado
        return self.estado.cidades.all()