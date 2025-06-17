from django import forms
from django.core.validators import EmailValidator

class ContactForm(forms.Form):
    """Formulário de contato"""
    
    name = forms.CharField(
        label='Nome',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome completo',
            'required': True,
        })
    )
    
    email = forms.EmailField(
        label='Email',
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'required': True,
        })
    )
    
    subject = forms.CharField(
        label='Assunto',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Assunto da mensagem',
            'required': True,
        })
    )
    
    message = forms.CharField(
        label='Mensagem',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Escreva sua mensagem aqui...',
            'rows': 5,
            'required': True,
        })
    )
    
    def clean_name(self):
        """Valida nome"""
        name = self.cleaned_data.get('name')
        if len(name.split()) < 2:
            raise forms.ValidationError('Por favor, informe seu nome completo.')
        return name
    
    def clean_message(self):
        """Valida mensagem"""
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError('A mensagem deve ter pelo menos 10 caracteres.')
        return message
