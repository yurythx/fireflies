from django import forms
from .models import Produto
from django.core.exceptions import ValidationError
from django.utils import timezone


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 'descricao', 'preco', 'categoria',
            'estoque', 'estoque_minimo', 'status', 'status_message',
            'imagem', 'promocao_inicio', 'promocao_fim'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'preco': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'estoque': forms.NumberInput(attrs={'min': '0'}),
            'estoque_minimo': forms.NumberInput(attrs={'min': '0'}),
            'promocao_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'promocao_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco < 0:
            raise ValidationError("O preço não pode ser negativo.")
        return preco

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('promocao_inicio')
        fim = cleaned_data.get('promocao_fim')

        if inicio and fim and inicio >= fim:
            raise ValidationError("A data de término da promoção deve ser posterior à de início.")

        if inicio and inicio < timezone.now():
            raise ValidationError("A data de início da promoção não pode estar no passado.")

        return cleaned_data