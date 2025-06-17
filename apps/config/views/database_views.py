"""
Views para gerenciamento de configurações de banco de dados
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import json

from apps.config.models.configuration_models import DatabaseConfiguration
from apps.config.forms.database_forms import (
    DatabaseConfigurationForm, 
    DatabaseTestForm, 
    DatabaseSelectionForm
)
from apps.config.mixins import ConfigPermissionMixin


def is_admin_user(user):
    """Verifica se o usuário é admin"""
    return user.is_authenticated and user.is_staff


class DatabaseConfigListView(ConfigPermissionMixin, ListView):
    """Lista de configurações de banco de dados"""
    model = DatabaseConfiguration
    template_name = 'config/database/list.html'
    context_object_name = 'configurations'
    paginate_by = 10
    
    def get_queryset(self):
        return DatabaseConfiguration.objects.all().order_by('-is_default', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Configurações de Banco de Dados',
            'breadcrumbs': [
                {'name': 'Configurações', 'url': '/config/'},
                {'name': 'Banco de Dados', 'url': None}
            ]
        })
        return context


class DatabaseConfigCreateView(ConfigPermissionMixin, CreateView):
    """Criar nova configuração de banco"""
    model = DatabaseConfiguration
    form_class = DatabaseConfigurationForm
    template_name = 'config/database/form.html'
    success_url = reverse_lazy('config:database_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Nova Configuração de Banco',
            'form_title': 'Adicionar Configuração de Banco de Dados',
            'breadcrumbs': [
                {'name': 'Configurações', 'url': '/config/'},
                {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
                {'name': 'Nova Configuração', 'url': None}
            ]
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Configuração de banco criada com sucesso!')
        return super().form_valid(form)


class DatabaseConfigUpdateView(ConfigPermissionMixin, UpdateView):
    """Editar configuração de banco"""
    model = DatabaseConfiguration
    form_class = DatabaseConfigurationForm
    template_name = 'config/database/form.html'
    success_url = reverse_lazy('config:database_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': f'Editar {self.object.name}',
            'form_title': f'Editar Configuração: {self.object.name}',
            'breadcrumbs': [
                {'name': 'Configurações', 'url': '/config/'},
                {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
                {'name': 'Editar', 'url': None}
            ]
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Configuração de banco atualizada com sucesso!')
        return super().form_valid(form)


class DatabaseConfigDeleteView(ConfigPermissionMixin, DeleteView):
    """Deletar configuração de banco"""
    model = DatabaseConfiguration
    template_name = 'config/database/delete.html'
    success_url = reverse_lazy('config:database_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': f'Excluir {self.object.name}',
            'breadcrumbs': [
                {'name': 'Configurações', 'url': '/config/'},
                {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
                {'name': 'Excluir', 'url': None}
            ]
        })
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Não permitir deletar configuração padrão
        if self.object.is_default:
            messages.error(request, 'Não é possível excluir a configuração padrão.')
            return redirect('config:database_list')
        
        messages.success(request, f'Configuração "{self.object.name}" excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
@user_passes_test(is_admin_user)
def database_test_connection(request, pk):
    """Testar conexão com banco de dados"""
    config = get_object_or_404(DatabaseConfiguration, pk=pk)
    
    if request.method == 'POST':
        success, message = config.test_connection()
        
        return JsonResponse({
            'success': success,
            'message': message,
            'last_tested': config.last_tested_at.isoformat() if config.last_tested_at else None
        })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@user_passes_test(is_admin_user)
def database_selection(request):
    """Seleção de banco padrão"""
    if request.method == 'POST':
        form = DatabaseSelectionForm(request.POST)
        if form.is_valid():
            try:
                config = form.save()
                messages.success(
                    request,
                    f'Configuração "{config.name}" definida como padrão com sucesso!'
                )

                if form.cleaned_data['update_env']:
                    success, message = config.update_env_file()
                    if success:
                        messages.success(request, message)
                        messages.info(
                            request,
                            'Reinicie o servidor para aplicar as mudanças nas variáveis de ambiente.'
                        )
                    else:
                        messages.warning(request, f'Configuração aplicada, mas houve problema ao atualizar .env: {message}')

                return redirect('config:database_list')
            except Exception as e:
                messages.error(request, f'Erro ao aplicar configuração: {str(e)}')
    else:
        form = DatabaseSelectionForm()
    
    context = {
        'form': form,
        'page_title': 'Selecionar Banco Padrão',
        'breadcrumbs': [
            {'name': 'Configurações', 'url': '/config/'},
            {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
            {'name': 'Selecionar Padrão', 'url': None}
        ]
    }
    
    return render(request, 'config/database/selection.html', context)


@login_required
@user_passes_test(is_admin_user)
def database_config_preview(request, pk):
    """Preview da configuração de banco para o .env"""
    config = get_object_or_404(DatabaseConfiguration, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'name': config.name,
            'engine': config.engine,
            'name_db': config.name_db,
            'user': config.user,
            'password': '***' if config.password else '',
            'host': config.host,
            'port': config.port,
        })

    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
@user_passes_test(is_admin_user)
def database_apply_production(request, pk):
    """Aplicar configuração para produção"""
    config = get_object_or_404(DatabaseConfiguration, pk=pk)

    if request.method == 'POST':
        try:
            # Remover padrão atual
            DatabaseConfiguration.objects.filter(is_default=True).update(is_default=False)

            # Definir novo padrão
            config.is_default = True
            config.save()

            # Atualizar arquivo .env
            success, message = config.update_env_file()

            if success:
                # Criar configuração específica para produção
                prod_config = {
                    'DB_ENGINE': config.engine,
                    'DB_NAME': config.name_db,
                    'DB_USER': config.user,
                    'DB_PASSWORD': config.password,
                    'DB_HOST': config.host or 'db',  # Default para Docker
                    'DB_PORT': config.port or ('5432' if 'postgresql' in config.engine else '3306'),
                }

                return JsonResponse({
                    'success': True,
                    'message': f'Configuração "{config.name}" aplicada para produção',
                    'env_updated': True,
                    'config': prod_config,
                    'restart_required': True
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao atualizar .env: {message}'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao aplicar configuração: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)


@login_required
@user_passes_test(is_admin_user)
def database_quick_setup(request):
    """Setup rápido de banco de dados"""
    if request.method == 'POST':
        db_type = request.POST.get('db_type')
        
        # Configurações pré-definidas
        presets = {
            'sqlite': {
                'name': 'SQLite Local',
                'engine': 'django.db.backends.sqlite3',
                'database_name': 'db.sqlite3',
                'host': '',
                'port': None,
                'username': '',
                'password': '',
            },
            'postgresql': {
                'name': 'PostgreSQL Local',
                'engine': 'django.db.backends.postgresql',
                'database_name': 'havoc_db',
                'host': 'localhost',
                'port': 5432,
                'username': 'postgres',
                'password': '',
            },
            'mysql': {
                'name': 'MySQL Local',
                'engine': 'django.db.backends.mysql',
                'database_name': 'havoc_db',
                'host': 'localhost',
                'port': 3306,
                'username': 'root',
                'password': '',
            }
        }
        
        if db_type in presets:
            preset = presets[db_type]
            
            # Criar configuração
            config = DatabaseConfiguration.objects.create(**preset)
            
            messages.success(
                request,
                f'Configuração "{config.name}" criada com sucesso! '
                f'Edite-a para ajustar os detalhes da conexão.'
            )
            
            return redirect('config:database_edit', pk=config.pk)
    
    context = {
        'page_title': 'Setup Rápido de Banco',
        'breadcrumbs': [
            {'name': 'Configurações', 'url': '/config/'},
            {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
            {'name': 'Setup Rápido', 'url': None}
        ]
    }
    
    return render(request, 'config/database/quick_setup.html', context)
