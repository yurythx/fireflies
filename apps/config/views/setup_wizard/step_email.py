from django.contrib import messages
from django.shortcuts import redirect

def process_step_email(request, wizard):
    email_backend = request.POST.get('email_backend')
    email_config = {'backend': email_backend}

    if email_backend == 'smtp':
        email_host = request.POST.get('email_host', '')
        email_port = request.POST.get('email_port', '')
        email_user = request.POST.get('email_user', '')
        email_password = request.POST.get('email_password', '')
        use_tls = request.POST.get('use_tls') == 'on'
        use_ssl = request.POST.get('use_ssl') == 'on'
        default_from = request.POST.get('default_from', '')

        # Validação
        if not all([email_host, email_port, email_user, email_password]):
            messages.error(request, "Preencha todos os campos SMTP obrigatórios!")
            return redirect('setup_wizard?step=3')

        email_config.update({
            'host': email_host,
            'port': email_port,
            'user': email_user,
            'password': email_password,
            'use_tls': use_tls,
            'use_ssl': use_ssl,
            'default_from': default_from,
        })
    else:
        # Console backend não precisa de campos extras
        pass

    wizard.save_progress('email', email_config)
    messages.success(request, "Configuração de email salva!")
    return redirect('setup_wizard?step=4') 