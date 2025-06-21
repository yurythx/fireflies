from ..base import WizardStepHandler
from django.contrib import messages
from django.shortcuts import redirect

class SecurityStepHandler(WizardStepHandler):
    def process(self, request, orchestrator):
        config = {
            'security_mode': request.POST.get('security_mode'),
            'allowed_hosts': request.POST.get('allowed_hosts'),
            'csrf_trusted_origins': request.POST.get('csrf_trusted_origins'),
            'security_level': request.POST.get('security_level'),
            'session_timeout': request.POST.get('session_timeout'),
            'enable_https': request.POST.get('enable_https') == 'on',
        }
        orchestrator.save_progress('security', config)
        messages.success(request, "Configuração de segurança salva!")
        return redirect('setup_wizard?step=5') 