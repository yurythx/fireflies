from django.contrib import messages
from django.shortcuts import redirect

def process_step_admin(request, wizard):
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    password_confirm = request.POST.get('password_confirm')
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')

    # Validação
    if not all([username, email, password, password_confirm]):
        messages.error(request, "Todos os campos obrigatórios devem ser preenchidos")
        return redirect('setup_wizard?step=2')
    if password != password_confirm:
        messages.error(request, "As senhas não coincidem")
        return redirect('setup_wizard?step=2')
    if len(password) < 8:
        messages.error(request, "A senha deve ter pelo menos 8 caracteres")
        return redirect('setup_wizard?step=2')

    admin_config = {
        'username': username,
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
    }
    wizard.save_progress('admin', admin_config)
    messages.success(request, "Configuração do administrador salva!")
    return redirect('setup_wizard?step=3') 