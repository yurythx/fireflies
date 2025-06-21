from ..base import WizardStepHandler
from django.contrib import messages
from django.shortcuts import redirect

class FinalizeStepHandler(WizardStepHandler):
    def process(self, request, orchestrator):
        # Aplica todas as configurações salvas
        success = orchestrator.apply_all_configurations()
        if success:
            messages.success(request, "Configuração finalizada com sucesso!")
            return redirect('config:dashboard')
        else:
            messages.error(request, "Erro ao finalizar configuração.")
            return redirect('setup_wizard?step=5') 