from django import forms
from .models import Cliente
from django.core.exceptions import ValidationError
import re

class ClienteForm(forms.ModelForm):
    """Formulário para o modelo Cliente."""

    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'cpf', 'cnpj', 'data_nascimento']
    

    def clean_cpf(self):
        """Validação personalizada para o campo CPF."""
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Valida se o CPF está no formato correto
            if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
                raise ValidationError("Formato de CPF inválido. Use XXX.XXX.XXX-XX")
        return cpf

    def clean_cnpj(self):
        """Validação personalizada para o campo CNPJ."""
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            # Valida se o CNPJ está no formato correto
            if not re.match(r'^\d{2}\.\d{3}\.\d{3}/0001-\d{2}$', cnpj):
                raise ValidationError("Formato de CNPJ inválido. Use XX.XXX.XXX/0001-XX")
        return cnpj

    def save(self, commit=True):
        """Salva o objeto Cliente, criando o slug automaticamente."""
        cliente = super().save(commit=False)
        if not cliente.slug:
            cliente.slug = cliente.nome.lower().replace(" ", "-")
        
        # Salvar o objeto no banco de dados
        if commit:
            cliente.save()
        
        return cliente