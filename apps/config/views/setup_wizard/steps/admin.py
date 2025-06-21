from ..base import WizardStepHandler
from django.contrib import messages
from django.shortcuts import redirect

class AdminStepHandler(WizardStepHandler):
    def process(self, request, orchestrator):
        config = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'password_confirm': request.POST.get('password_confirm'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
        }
        # Validação simples
        if not config['username'] or not config['email'] or not config['password']:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return redirect('setup_wizard?step=2')
        if config['password'] != config['password_confirm']:
            messages.error(request, "As senhas não coincidem.")
            return redirect('setup_wizard?step=2')
        orchestrator.save_progress('admin', config)
        messages.success(request, "Configuração do administrador salva!")
        return redirect('setup_wizard?step=3') 