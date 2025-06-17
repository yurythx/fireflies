from django.shortcuts import render
from django.views import View
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from apps.pages.forms.contact_forms import ContactForm

class AboutView(View):
    """View para página Sobre"""
    template_name = 'pages/about.html'
    
    def get(self, request):
        """Exibe página sobre"""
        context = {
            'meta_title': 'Sobre Nós',
            'meta_description': 'Conheça mais sobre nossa empresa e nossa missão',
        }
        return render(request, self.template_name, context)


class ContactView(View):
    """View para página de contato"""
    template_name = 'pages/contact.html'
    
    def get(self, request):
        """Exibe formulário de contato"""
        form = ContactForm()
        context = {
            'form': form,
            'meta_title': 'Contato',
            'meta_description': 'Entre em contato conosco',
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Processa formulário de contato"""
        form = ContactForm(request.POST)
        
        if form.is_valid():
            try:
                # Dados do formulário
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
                
                # Monta email
                email_subject = f"Contato do site: {subject}"
                email_message = f"""
                Nome: {name}
                Email: {email}
                Assunto: {subject}
                
                Mensagem:
                {message}
                """
                
                # Envia email
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
                form = ContactForm()  # Limpa o formulário
                
            except Exception as e:
                messages.error(request, 'Erro ao enviar mensagem. Tente novamente.')
        
        context = {
            'form': form,
            'meta_title': 'Contato',
            'meta_description': 'Entre em contato conosco',
        }
        return render(request, self.template_name, context)


class PrivacyView(View):
    """View para política de privacidade"""
    template_name = 'pages/privacy.html'
    
    def get(self, request):
        """Exibe política de privacidade"""
        context = {
            'meta_title': 'Política de Privacidade',
            'meta_description': 'Nossa política de privacidade e proteção de dados',
        }
        return render(request, self.template_name, context)


class TermsView(View):
    """View para termos de uso"""
    template_name = 'pages/terms.html'
    
    def get(self, request):
        """Exibe termos de uso"""
        context = {
            'meta_title': 'Termos de Uso',
            'meta_description': 'Termos e condições de uso do site',
        }
        return render(request, self.template_name, context)
