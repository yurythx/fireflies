from django import forms
from .models import Endereco, Estado, Cidade


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['rua', 'numero', 'complemento', 'bairro', 'estado', 'cidade', 'cep']

    # Exemplo de forma correta de manipular os dados de "estado" e "cidade" no formulário
    def __init__(self, *args, **kwargs):
        super(EnderecoForm, self).__init__(*args, **kwargs)
        # Aqui você pode preencher as cidades dinamicamente com base no estado, se necessário
        if 'estado' in self.fields:
            self.fields['estado'].queryset = Estado.objects.all()  # Exemplo: filtro de estados
        if 'cidade' in self.fields:
            self.fields['cidade'].queryset = Cidade.objects.none()  # Cidade ficará vazio até escolher um estado