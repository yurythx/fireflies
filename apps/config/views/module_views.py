from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, UpdateView
from django.views import View
from django.http import JsonResponse
from apps.config.models.app_module_config import AppModuleConfiguration
from apps.config.services.module_service import ModuleService
from apps.config.forms.module_forms import ModuleConfigurationForm


class ModuleListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Lista e gerencia todos os módulos do sistema com funcionalidades de teste integradas"""
    template_name = 'config/modules/list.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        """Exibe página de gerenciamento de módulos com testes integrados"""
        module_service = ModuleService()

        # Obtém todos os módulos
        all_modules = module_service.get_all_modules()
        enabled_modules = module_service.get_enabled_modules()
        disabled_modules = [m for m in all_modules if not m.is_available]

        # Testa URLs dos módulos
        module_tests = []
        for module in all_modules:
            test_result = self._test_module_access(module)
            module_tests.append({
                'module': module,
                'test_result': test_result
            })

        # Estatísticas
        module_stats = module_service.get_module_statistics()

        context = {
            'modules': all_modules,
            'enabled_modules': enabled_modules,
            'disabled_modules': disabled_modules,
            'module_tests': module_tests,
            'module_stats': module_stats,
            'page_title': 'Gerenciamento de Módulos',
            'page_description': 'Configure e teste os módulos do sistema',
        }

        return render(request, self.template_name, context)

    def post(self, request):
        """Processa ações de gerenciamento e teste"""
        action = request.POST.get('action')
        module_name = request.POST.get('module_name')

        if not action or not module_name:
            messages.error(request, 'Ação ou módulo não especificado.')
            return redirect('config:module_list')

        module_service = ModuleService()

        if action == 'toggle':
            success = self._handle_toggle_module(module_service, module_name, request.user)
        elif action == 'test_access':
            success = self._handle_test_access(module_service, module_name)
        elif action == 'enable':
            success = module_service.enable_module(module_name, request.user)
            if success:
                messages.success(request, f'Módulo habilitado com sucesso.')
            else:
                messages.error(request, f'Erro ao habilitar módulo.')
        elif action == 'disable':
            success = module_service.disable_module(module_name, request.user)
            if success:
                messages.success(request, f'Módulo desabilitado com sucesso.')
            else:
                messages.error(request, f'Erro ao desabilitar módulo.')
        else:
            messages.error(request, 'Ação não reconhecida.')

        return redirect('config:module_list')

    def _handle_toggle_module(self, module_service, module_name, user):
        """Alterna status do módulo"""
        module = module_service.get_module_by_name(module_name)
        if not module:
            messages.error(self.request, f'Módulo {module_name} não encontrado.')
            return False

        if module.is_core:
            messages.error(self.request, f'Módulo {module.display_name} é principal e não pode ser desabilitado.')
            return False

        if module.is_enabled:
            success = module_service.disable_module(module_name, user)
            action = 'desabilitado'
        else:
            success = module_service.enable_module(module_name, user)
            action = 'habilitado'

        if success:
            messages.success(self.request, f'Módulo {module.display_name} {action} com sucesso.')
        else:
            messages.error(self.request, f'Erro ao alterar status do módulo {module.display_name}.')

        return success

    def _handle_test_access(self, module_service, module_name):
        """Testa acesso ao módulo"""
        module = module_service.get_module_by_name(module_name)
        if module:
            test_result = self._test_module_access(module)
            if test_result['accessible']:
                messages.success(self.request, f'Módulo {module.display_name} está acessível.')
            else:
                messages.warning(self.request, f'Módulo {module.display_name} não está acessível: {test_result["reason"]}')
            return True
        else:
            messages.error(self.request, f'Módulo {module_name} não encontrado.')
            return False

    def _test_module_access(self, module):
        """Testa se um módulo está acessível"""
        try:
            # Verifica se está habilitado
            if not module.is_available:
                return {
                    'accessible': False,
                    'reason': 'Módulo desabilitado',
                    'status': 'disabled'
                }

            # Verifica dependências
            if module.dependencies:
                module_service = ModuleService()
                for dep in module.dependencies:
                    dep_module = module_service.get_module_by_name(dep)
                    if not dep_module or not dep_module.is_available:
                        return {
                            'accessible': False,
                            'reason': f'Dependência {dep} não disponível',
                            'status': 'dependency_error'
                        }

            # Verifica se a URL está configurada
            if not module.url_pattern:
                return {
                    'accessible': True,
                    'reason': 'Módulo sem URL específica',
                    'status': 'no_url'
                }

            return {
                'accessible': True,
                'reason': 'Módulo totalmente funcional',
                'status': 'ok'
            }

        except Exception as e:
            return {
                'accessible': False,
                'reason': f'Erro interno: {str(e)}',
                'status': 'error'
            }


class ModuleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detalhes de um módulo específico"""
    model = AppModuleConfiguration
    template_name = 'config/modules/detail.html'
    context_object_name = 'module'
    slug_field = 'app_name'
    slug_url_kwarg = 'app_name'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_service = ModuleService()
        
        # Valida dependências
        dependencies_info = module_service.validate_module_dependencies(
            self.object.app_name
        )
        
        # Busca módulos dependentes
        dependent_modules = self.object.get_dependent_modules()
        
        context.update({
            'dependencies_info': dependencies_info,
            'dependent_modules': dependent_modules,
            'page_title': f'Módulo: {self.object.display_name}',
        })
        return context


class ModuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edita configurações de um módulo"""
    model = AppModuleConfiguration
    form_class = ModuleConfigurationForm
    template_name = 'config/modules/update.html'
    slug_field = 'app_name'
    slug_url_kwarg = 'app_name'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(
            self.request,
            f'Módulo "{form.instance.display_name}" atualizado com sucesso!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        from django.urls import reverse
        return reverse('config:module_detail', kwargs={'app_name': self.object.app_name})


class ModuleToggleView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Habilita/desabilita um módulo"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request, app_name):
        module_service = ModuleService()
        module = get_object_or_404(AppModuleConfiguration, app_name=app_name)
        
        # Não permite desabilitar módulos principais
        if module.is_core and not module.is_enabled:
            messages.error(
                request,
                f'O módulo "{module.display_name}" é principal e não pode ser desabilitado.'
            )
            return redirect('config:module_list')
        
        action = request.POST.get('action')
        success = False
        
        if action == 'enable':
            success = module_service.enable_module(app_name, request.user)
            action_text = 'habilitado'
        elif action == 'disable':
            success = module_service.disable_module(app_name, request.user)
            action_text = 'desabilitado'
        else:
            messages.error(request, 'Ação inválida.')
            return redirect('config:module_list')
        
        if success:
            messages.success(
                request,
                f'Módulo "{module.display_name}" {action_text} com sucesso!'
            )
        else:
            messages.error(
                request,
                f'Erro ao {action_text.replace("o", "ar")} o módulo "{module.display_name}".'
            )
        
        return redirect('config:module_list')





class ModuleStatsAPIView(LoginRequiredMixin, UserPassesTestMixin, View):
    """API para estatísticas dos módulos"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get(self, request):
        module_service = ModuleService()
        stats = module_service.get_module_statistics()
        
        # Adiciona informações detalhadas
        modules_by_type = {}
        for module in AppModuleConfiguration.objects.all():
            module_type = module.get_module_type_display()
            if module_type not in modules_by_type:
                modules_by_type[module_type] = {'total': 0, 'enabled': 0}
            
            modules_by_type[module_type]['total'] += 1
            if module.is_enabled:
                modules_by_type[module_type]['enabled'] += 1
        
        stats['by_type'] = modules_by_type
        
        return JsonResponse(stats)


class ModuleDependencyCheckView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Verifica dependências de um módulo"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, app_name):
        module_service = ModuleService()
        dependencies_info = module_service.validate_module_dependencies(app_name)

        return JsonResponse(dependencies_info)
