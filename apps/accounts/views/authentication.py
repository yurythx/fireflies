from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from apps.accounts.forms.authentication import FlexibleLoginForm

@method_decorator([csrf_protect, never_cache], name='dispatch')
class LoginView(View):
    """View para login de usuários com suporte a email e username"""
    template_name = 'accounts/login.html'
    form_class = FlexibleLoginForm

    def get(self, request):
        """Exibe o formulário de login"""
        if request.user.is_authenticated:
            messages.info(request, '✅ Você já está logado.')
            return redirect('pages:home')

        # Verificar se há contexto de tentativa de acesso
        login_context = request.session.get('login_context', {})
        if login_context:
            attempted_area = login_context.get('attempted_area', 'esta área')
            messages.info(
                request,
                f'🔐 Para acessar {attempted_area}, faça login com seu e-mail ou nome de usuário.'
            )
            # Limpar contexto após usar
            del request.session['login_context']

        form = self.form_class(request=request)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Processa o login com formulário flexível"""
        form = self.form_class(request=request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            # Verificar "lembrar de mim"
            remember_me = form.cleaned_data.get('remember_me', False)
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semanas
            else:
                request.session.set_expiry(0)  # Fechar ao fechar navegador

            # Fazer login
            login(request, user)

            # Mensagem personalizada baseada no horário
            greeting = self.get_greeting()
            name = user.get_full_name() or user.first_name or user.username

            messages.success(
                request,
                f'🎉 {greeting}, {name}! Login realizado com sucesso.'
            )

            # Redirecionar para página solicitada ou home
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('pages:home')

        # Se formulário inválido, renderizar com erros
        return render(request, self.template_name, {'form': form})

    def get_greeting(self):
        """Retorna saudação baseada no horário"""
        from datetime import datetime
        hour = datetime.now().hour

        if 5 <= hour < 12:
            return "Bom dia"
        elif 12 <= hour < 18:
            return "Boa tarde"
        else:
            return "Boa noite"

class LogoutView(View):
    """View para logout de usuários"""

    def get(self, request):
        """Processa o logout"""
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, 'Você foi desconectado com sucesso.')
        return redirect('pages:home')

    def post(self, request):
        """Processa o logout via POST"""
        return self.get(request)