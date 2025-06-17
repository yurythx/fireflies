from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from apps.config.forms.user_forms import UserCreateForm, UserUpdateForm, UserSearchForm
from apps.config.services.user_management_service import UserManagementService
from apps.config.services.system_config_service import AuditLogService
from apps.config.repositories.user_repository import DjangoUserRepository
from apps.config.repositories.config_repository import DjangoAuditLogRepository
from apps.config.mixins import ConfigPermissionMixin, PermissionHelperMixin, SuperuserRequiredMixin

User = get_user_model()

class UserListView(ConfigPermissionMixin, PermissionHelperMixin, View):
    """View para listar usuários"""
    template_name = 'config/users/list.html'

    def get(self, request):
        """Lista usuários com filtros e busca"""
        form = UserSearchForm(request.GET)
        users = User.objects.all()

        # Aplica filtros
        if form.is_valid():
            query = form.cleaned_data.get('query')
            is_active = form.cleaned_data.get('is_active')
            is_staff = form.cleaned_data.get('is_staff')
            is_superuser = form.cleaned_data.get('is_superuser')

            if query:
                users = users.filter(
                    Q(email__icontains=query) |
                    Q(username__icontains=query) |
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query)
                )

            if is_active:
                users = users.filter(is_active=is_active == 'true')

            if is_staff:
                users = users.filter(is_staff=is_staff == 'true')

            if is_superuser:
                users = users.filter(is_superuser=is_superuser == 'true')

        # Paginação
        paginator = Paginator(users.order_by('-date_joined'), 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'form': form,
            'page_obj': page_obj,
            'users': page_obj.object_list,
        }

        return render(request, self.template_name, context)


class UserCreateView(ConfigPermissionMixin, PermissionHelperMixin, View):
    """View para criar usuários"""
    template_name = 'config/users/create.html'

    def get(self, request):
        """Exibe formulário de criação"""
        form = UserCreateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Processa criação do usuário"""
        form = UserCreateForm(request.POST)

        if form.is_valid():
            try:
                # Prepara dados do usuário
                user_data = {
                    'email': form.cleaned_data['email'],
                    'username': form.cleaned_data['username'],
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'password': form.cleaned_data['password1'],
                    'is_active': form.cleaned_data['is_active'],
                    'is_staff': form.cleaned_data['is_staff'],
                    'is_superuser': form.cleaned_data['is_superuser'],
                }

                # Cria o usuário usando o service
                audit_service = AuditLogService(DjangoAuditLogRepository())
                user_service = UserManagementService(DjangoUserRepository(), audit_service)

                user = user_service.create_user(user_data, request.user)

                # Atribui grupos
                groups = form.cleaned_data.get('groups', [])
                if groups:
                    user.groups.set(groups)

                name = user.get_full_name() or user.first_name or user.email
                messages.success(
                    request,
                    f'🎉 Usuário {name} criado com sucesso! Email: {user.email}'
                )
                return redirect('config:user_detail', slug=user.slug)

            except ValueError as e:
                error_msg = f'❌ Erro de validação: {str(e)}'
                messages.error(request, error_msg)
                form.add_error(None, str(e))
            except Exception as e:
                error_msg = f'🔧 Erro interno: {str(e)}. Tente novamente em alguns instantes.'
                messages.error(request, error_msg)
                form.add_error(None, 'Erro interno. Tente novamente.')

        return render(request, self.template_name, {'form': form})


class UserDetailView(ConfigPermissionMixin, PermissionHelperMixin, View):
    """View para visualizar detalhes do usuário"""
    template_name = 'config/users/detail.html'

    def get(self, request, slug):
        """Exibe detalhes do usuário"""
        try:
            user = User.objects.get(slug=slug)
            context = {
                'user_detail': user,
                'groups': user.groups.all(),
                'permissions': user.user_permissions.all(),
            }
            return render(request, self.template_name, context)
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            return redirect('config:user_list')


class UserUpdateView(ConfigPermissionMixin, PermissionHelperMixin, View):
    """View para editar usuários"""
    template_name = 'config/users/update.html'

    def get(self, request, slug):
        """Exibe formulário de edição"""
        try:
            user = User.objects.get(slug=slug)
            form = UserUpdateForm(instance=user)
            return render(request, self.template_name, {'form': form, 'user_detail': user})
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            return redirect('config:user_list')

    def post(self, request, slug):
        """Processa edição do usuário"""
        try:
            user = User.objects.get(slug=slug)
            form = UserUpdateForm(request.POST, instance=user)

            if form.is_valid():
                try:
                    # Atualiza dados básicos
                    updated_user = form.save()

                    # Atualiza grupos
                    groups = form.cleaned_data.get('groups', [])
                    updated_user.groups.set(groups)

                    # Log da ação
                    audit_service = AuditLogService(DjangoAuditLogRepository())
                    audit_service.log_user_action(
                        user=request.user,
                        action='UPDATE_USER',
                        target_user=updated_user,
                        description=f'Usuário {updated_user.email} atualizado'
                    )

                    name = updated_user.get_full_name() or updated_user.first_name or updated_user.email
                    messages.success(
                        request,
                        f'✅ Usuário {name} atualizado com sucesso!'
                    )
                    return redirect('config:user_detail', slug=updated_user.slug)

                except Exception as e:
                    error_msg = f'🔧 Erro ao atualizar usuário: {str(e)}'
                    messages.error(request, error_msg)
                    form.add_error(None, f'Erro ao atualizar usuário: {str(e)}')

            return render(request, self.template_name, {'form': form, 'user_detail': user})

        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            return redirect('config:user_list')


class UserDeleteView(SuperuserRequiredMixin, PermissionHelperMixin, View):
    """View para deletar usuários - Apenas superusuários"""
    template_name = 'config/users/delete.html'

    def get(self, request, slug):
        """Exibe confirmação de exclusão"""
        try:
            user = User.objects.get(slug=slug)

            # Não permite deletar o próprio usuário
            if user == request.user:
                messages.error(request, 'Você não pode deletar sua própria conta.')
                return redirect('config:user_list')

            # Não permite deletar superusuários (exceto por outros superusuários)
            if user.is_superuser and not request.user.is_superuser:
                messages.error(request, 'Você não tem permissão para deletar superusuários.')
                return redirect('config:user_list')

            return render(request, self.template_name, {'user_detail': user})
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            return redirect('config:user_list')

    def post(self, request, slug):
        """Processa exclusão do usuário"""
        try:
            user = User.objects.get(slug=slug)

            # Validações de segurança
            if user == request.user:
                messages.error(request, 'Você não pode deletar sua própria conta.')
                return redirect('config:user_list')

            if user.is_superuser and not request.user.is_superuser:
                messages.error(request, 'Você não tem permissão para deletar superusuários.')
                return redirect('config:user_list')

            # Salva informações para o log antes de deletar
            user_email = user.email

            # Deleta o usuário
            user.delete()

            # Log da ação
            audit_service = AuditLogService(DjangoAuditLogRepository())
            audit_service.log_user_action(
                user=request.user,
                action='DELETE_USER',
                description=f'Usuário {user_email} deletado',
                extra_data={'deleted_user_email': user_email}
            )

            messages.success(request, f'🗑️ Usuário {user_email} deletado com sucesso!')
            return redirect('config:user_list')

        except User.DoesNotExist:
            messages.error(request, '❌ Usuário não encontrado.')
            return redirect('config:user_list')
        except Exception as e:
            messages.error(request, f'🔧 Erro ao deletar usuário: {str(e)}')
            return redirect('config:user_list')
