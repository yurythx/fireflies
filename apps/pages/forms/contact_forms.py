from django import forms
from django.core.mail import send_mail
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div, Field
from crispy_forms.bootstrap import FormActions


class ContactForm(forms.Form):
    """Formulário de contato"""
    
    SUBJECT_CHOICES = [
        ('', 'Selecione um assunto'),
        ('general', 'Informações Gerais'),
        ('support', 'Suporte Técnico'),
        ('business', 'Parcerias/Negócios'),
        ('feedback', 'Feedback'),
        ('other', 'Outro'),
    ]
    
    name = forms.CharField(
        label='Nome completo',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu nome completo',
            'autocomplete': 'name'
        })
    )

    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'seu@email.com',
            'autocomplete': 'email'
        })
    )

    phone = forms.CharField(
        label='Telefone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '(11) 99999-9999',
            'autocomplete': 'tel'
        })
    )
    
    subject = forms.ChoiceField(
        label='Assunto',
        choices=SUBJECT_CHOICES,
        widget=forms.Select()
    )
    
    message = forms.CharField(
        label='Mensagem',
        widget=forms.Textarea(attrs={
            'placeholder': 'Digite sua mensagem...',
            'rows': 6
        })
    )
    
    newsletter = forms.BooleanField(
        label='Quero receber newsletter',
        required=False,
        help_text='Receba novidades e atualizações por e-mail'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        self.helper.layout = Layout(
            HTML('<div class="row">'),
            Column('name', css_class='col-md-6'),
            Column('email', css_class='col-md-6'),
            HTML('</div>'),
            HTML('<div class="row">'),
            Column('phone', css_class='col-md-6'),
            Column('subject', css_class='col-md-6'),
            HTML('</div>'),
            'message',
            'newsletter',
            HTML('<div class="d-grid gap-2 mt-4">'),
            Submit('submit', 'Enviar Mensagem', css_class='btn btn-primary btn-lg'),
            HTML('</div>'),
            HTML('<div class="text-center mt-3">'),
            HTML('<small class="text-muted">Responderemos em até 24 horas</small>'),
            HTML('</div>')
        )

    def clean_phone(self):
        """Valida o telefone se fornecido"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove caracteres não numéricos
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) < 10:
                raise forms.ValidationError('Telefone deve ter pelo menos 10 dígitos.')
        return phone

    def send_email(self):
        """Envia o e-mail de contato"""
        if self.is_valid():
            name = self.cleaned_data['name']
            email = self.cleaned_data['email']
            phone = self.cleaned_data.get('phone', 'Não informado')
            subject = dict(self.SUBJECT_CHOICES)[self.cleaned_data['subject']]
            message = self.cleaned_data['message']
            newsletter = self.cleaned_data.get('newsletter', False)
            
            # Monta o corpo do e-mail
            email_body = f"""
Nova mensagem de contato recebida:

Nome: {name}
E-mail: {email}
Telefone: {phone}
Assunto: {subject}
Newsletter: {'Sim' if newsletter else 'Não'}

Mensagem:
{message}

---
Enviado através do formulário de contato do site.
            """
            
            try:
                send_mail(
                    subject=f'[Contato] {subject} - {name}',
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL if hasattr(settings, 'CONTACT_EMAIL') else 'contato@havoc.com'],
                    fail_silently=False,
                )
                return True
            except Exception as e:
                return False
        return False


class NewsletterForm(forms.Form):
    """Formulário de newsletter"""
    
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Digite seu e-mail',
            'autocomplete': 'email'
        })
    )

    name = forms.CharField(
        label='Nome',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Seu nome (opcional)',
            'autocomplete': 'name'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'd-flex'
        
        self.helper.layout = Layout(
            Field('email', css_class='form-control me-2'),
            Submit('submit', 'Inscrever', css_class='btn btn-primary')
        )


class SearchForm(forms.Form):
    """Formulário de busca geral"""
    
    q = forms.CharField(
        label='Buscar',
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite sua busca...'
        })
    )
    
    category = forms.ChoiceField(
        label='Categoria',
        choices=[
            ('', 'Todas as categorias'),
            ('articles', 'Artigos'),
            ('pages', 'Páginas'),
            ('users', 'Usuários'),
        ],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'd-flex'
        
        self.helper.layout = Layout(
            Field('q', css_class='form-control me-2'),
            Field('category', css_class='form-select me-2', style='width: auto;'),
            Submit('submit', 'Buscar', css_class='btn btn-outline-primary')
        )
