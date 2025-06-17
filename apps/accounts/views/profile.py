from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.accounts.forms.profile_forms import (
    ProfileUpdateForm, AvatarUpdateForm, EmailUpdateForm, PasswordChangeForm
)
from apps.accounts.services.profile_service import ProfileService
from apps.accounts.repositories.user_repository import DjangoUserRepository
import os

User = get_user_model()

class UserProfileView(LoginRequiredMixin, View):
    """View para exibir perfil do usuário"""
    template_name = 'accounts/profile.html'
    login_url = '/accounts/login/'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Injeção de dependência
        self.profile_service = ProfileService(DjangoUserRepository())

    def get(self, request, slug=None):
        """Exibe o perfil do usuário"""
        try:
            if slug:
                # Se slug foi fornecido, busca o usuário pelo slug
                user = self.profile_service.get_profile(slug)
            else:
                # Se não há slug, mostra o perfil do usuário logado
                user = request.user

            context = {
                'profile_user': user,
                'avatar_form': AvatarUpdateForm(instance=user),
                'user_stats': self.profile_service.get_user_statistics(user),
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f'Erro ao carregar perfil: {str(e)}')
            return redirect('accounts:profile')

class UserUpdateView(LoginRequiredMixin, View):
    """View para editar perfil do usuário"""
    template_name = 'accounts/user_settings.html'
    login_url = '/accounts/login/'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Injeção de dependência
        self.profile_service = ProfileService(DjangoUserRepository())

    def get(self, request):
        """Exibe o formulário de edição"""
        user = request.user
        context = {
            'profile_form': ProfileUpdateForm(instance=user),
            'avatar_form': AvatarUpdateForm(instance=user),
            'email_form': EmailUpdateForm(user=user, instance=user),
            'password_form': PasswordChangeForm(user=user),
            'profile_user': user,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Processa a edição do perfil"""
        user = request.user
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            return self.handle_profile_update(request, user)
        elif form_type == 'avatar':
            return self.handle_avatar_update(request, user)
        elif form_type == 'email':
            return self.handle_email_update(request, user)
        elif form_type == 'password':
            return self.handle_password_change(request, user)

        messages.error(request, 'Tipo de formulário inválido.')
        return redirect('accounts:settings')

    def handle_profile_update(self, request, user):
        """Processa atualização do perfil usando ProfileService"""
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            try:
                # Usar ProfileService para atualizar o perfil
                updated_user = self.profile_service.update_profile(user, form.cleaned_data)
                messages.success(request, '🎉 Perfil atualizado com sucesso! Suas informações foram salvas.')
                return redirect('accounts:profile')
            except Exception as e:
                messages.error(request, f'❌ Erro ao atualizar perfil: {str(e)}')
        else:
            # Coletar erros específicos para mensagem mais detalhada
            error_fields = []
            for field, errors in form.errors.items():
                if field != '__all__':
                    error_fields.append(form.fields[field].label or field)

            if error_fields:
                fields_text = ', '.join(error_fields)
                messages.error(request, f'❌ Erro nos campos: {fields_text}. Verifique os dados e tente novamente.')
            else:
                messages.error(request, '❌ Erro ao atualizar perfil. Verifique os dados informados.')

            context = self.get_context_with_forms(user, profile_form=form)
            return render(request, self.template_name, context)

    def handle_avatar_update(self, request, user):
        """Processa atualização do avatar"""
        form = AvatarUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '📸 Foto de perfil atualizada com sucesso! Sua nova imagem está linda!')
            return redirect('accounts:profile')
        else:
            # Verificar tipo específico de erro
            avatar_errors = form.errors.get('avatar', [])
            if avatar_errors:
                error_msg = avatar_errors[0]
                messages.error(request, f'❌ Erro no upload da imagem: {error_msg}')
            else:
                messages.error(request, '❌ Erro ao atualizar foto de perfil. Verifique o arquivo selecionado.')

            context = self.get_context_with_forms(user, avatar_form=form)
            return render(request, self.template_name, context)

    def handle_email_update(self, request, user):
        """Processa atualização do email"""
        form = EmailUpdateForm(user=user, data=request.POST, instance=user)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            # Aqui você implementaria o envio do código de verificação
            messages.success(request, f'📧 Código de verificação enviado para {new_email}! Verifique sua caixa de entrada.')
            return redirect('accounts:profile')
        else:
            # Verificar erros específicos
            email_errors = form.errors.get('email', [])
            password_errors = form.errors.get('current_password', [])

            if email_errors:
                messages.error(request, f'❌ Erro no e-mail: {email_errors[0]}')
            elif password_errors:
                messages.error(request, f'❌ Erro na senha: {password_errors[0]}')
            else:
                messages.error(request, '❌ Erro ao alterar e-mail. Verifique os dados informados.')

            context = self.get_context_with_forms(user, email_form=form)
            return render(request, self.template_name, context)

    def handle_password_change(self, request, user):
        """Processa alteração de senha"""
        form = PasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            update_session_auth_hash(request, user)  # Mantém o usuário logado
            messages.success(request, '🔒 Senha alterada com sucesso! Sua conta está mais segura agora.')
            return redirect('accounts:profile')
        else:
            # Verificar erros específicos
            current_password_errors = form.errors.get('current_password', [])
            new_password1_errors = form.errors.get('new_password1', [])
            new_password2_errors = form.errors.get('new_password2', [])

            if current_password_errors:
                messages.error(request, f'❌ Erro na senha atual: {current_password_errors[0]}')
            elif new_password1_errors:
                messages.error(request, f'❌ Erro na nova senha: {new_password1_errors[0]}')
            elif new_password2_errors:
                messages.error(request, f'❌ Erro na confirmação: {new_password2_errors[0]}')
            else:
                messages.error(request, '❌ Erro ao alterar senha. Verifique os dados informados.')

            context = self.get_context_with_forms(user, password_form=form)
            return render(request, self.template_name, context)

    def get_context_with_forms(self, user, **kwargs):
        """Retorna contexto com todos os formulários"""
        context = {
            'profile_form': kwargs.get('profile_form', ProfileUpdateForm(instance=user)),
            'avatar_form': kwargs.get('avatar_form', AvatarUpdateForm(instance=user)),
            'email_form': kwargs.get('email_form', EmailUpdateForm(user=user, instance=user)),
            'password_form': kwargs.get('password_form', PasswordChangeForm(user=user)),
            'profile_user': user,
        }
        return context

class RemoveAvatarView(LoginRequiredMixin, View):
    """View para remover avatar do usuário"""
    login_url = '/accounts/login/'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Injeção de dependência
        self.profile_service = ProfileService(DjangoUserRepository())

    def post(self, request):
        """Remove o avatar do usuário usando ProfileService"""
        user = request.user

        try:
            success = self.profile_service.remove_avatar(user)
            if success:
                messages.success(request, '🗑️ Foto de perfil removida com sucesso! Agora você está usando o avatar padrão.')
            else:
                messages.info(request, 'ℹ️ Você não possui foto de perfil para remover.')
        except Exception as e:
            messages.error(request, f'❌ Erro ao remover foto de perfil: {str(e)}')

        return redirect('accounts:settings')
