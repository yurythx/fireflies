from django.contrib import messages
from django.shortcuts import redirect

def process_step_security(request, wizard):
    security_mode = request.POST.get('security_mode', 'open')
    if security_mode == 'open':
        # Valores padrão para ambiente de desenvolvimento
        security_config = {
            'allowed_hosts': '*',
            'csrf_trusted_origins': '*',
            'security_level': 'standard',
            'enable_https': False,
            'session_timeout': 3600,
            'mode': 'open',
        }
    else:
        security_config = {
            'allowed_hosts': request.POST.get('allowed_hosts', ''),
            'csrf_trusted_origins': request.POST.get('csrf_trusted_origins', ''),
            'security_level': request.POST.get('security_level', 'standard'),
            'enable_https': request.POST.get('enable_https') == 'on',
            'session_timeout': request.POST.get('session_timeout', '3600'),
            'mode': 'manual',
        }
    wizard.save_progress('security', security_config)
    messages.success(request, "Configurações de segurança salvas!")
    return redirect('setup_wizard?step=5') 