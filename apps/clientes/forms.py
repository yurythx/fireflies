from django import forms
from .models import Cliente
from apps.enderecos.models import Endereco


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'cpf']


class ClienteUpdateForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'cpf', 'data_nascimento', 'endereco']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    endereco = forms.ModelChoiceField(queryset=Endereco.objects.all(), required=False)