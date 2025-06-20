from django.contrib import messages
from django.shortcuts import redirect
from pathlib import Path
from django.conf import settings
from django.core.cache import cache
import logging

def process_step_finalize(request, wizard):
    try:
        if not wizard.apply_all_configurations():
            messages.error(request, "Erro ao aplicar configurações")
            return redirect('setup_wizard?step=5')
        cache.delete('setup_wizard_progress')
        first_install_file = Path(settings.BASE_DIR) / '.first_install'
        if first_install_file.exists():
            first_install_file.unlink()
        messages.success(request, "Configuração concluída com sucesso!")
        return redirect('/')
    except Exception as e:
        logging.error(f"Erro na finalização: {e}", exc_info=True)
        messages.error(request, f"Erro na finalização: {str(e)}")
        return redirect('setup_wizard?step=5') 