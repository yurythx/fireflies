# forms.py
import re
from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    """Formulário para o modelo Cliente com validações customizadas."""

    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'cpf', 'data_nascimento']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_telefone(self):
        """Valida o formato do telefone brasileiro: (XX) XXXX-XXXX ou (XX) XXXXX-XXXX."""
        telefone = self.cleaned_data.get('telefone', '').strip()

        # Expressão regular para telefone fixo e celular
        padrao = r'^\(\d{2}\)\s?\d{4,5}-\d{4}$'
        if not re.match(padrao, telefone):
            raise forms.ValidationError(
                'Formato inválido. Use (XX) XXXX-XXXX ou (XX) XXXXX-XXXX.'
            )
        return telefone

    def clean_cpf(self):
        """Valida o CPF no formato XXX.XXX.XXX-XX e com quantidade correta de dígitos."""
        cpf = self.cleaned_data.get('cpf', '').strip()

        padrao = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'
        if not re.match(padrao, cpf):
            raise forms.ValidationError(
                'Formato inválido. Use XXX.XXX.XXX-XX.'
            )

        # Remove pontos e traço para validar apenas os números
        numeros = re.sub(r'\D', '', cpf)

        if len(numeros) != 11 or len(set(numeros)) == 1:
            raise forms.ValidationError('CPF inválido.')

        return cpf


