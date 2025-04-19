from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomUserChangeForm
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

class AjaxListMixin:
    partial_template_name = None

    def render_to_response(self, context, **response_kwargs):
        if is_ajax(self.request) and self.partial_template_name:
            return render(self.request, self.partial_template_name, context)
        return super().render_to_response(context, **response_kwargs)

class AjaxFormMixin:
    template_name_ajax = None

    def form_invalid(self, form):
        if is_ajax(self.request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        if is_ajax(self.request):
            return JsonResponse({'success': True, 'message': 'Operação realizada com sucesso!'})
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            try:
                self.object = self.get_object()
            except AttributeError:
                self.object = None
            context = self.get_context_data()
            return render(request, self.template_name_ajax or self.template_name, context)
        return super().get(request, *args, **kwargs)

class CustomUserListView(AjaxListMixin, ListView):
    model = User
    template_name = 'accounts/lista_usuarios.html'
    partial_template_name = 'accounts/_lista_usuarios.html'
    context_object_name = 'accounts'
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        nome = self.request.GET.get('nome', '')
        email = self.request.GET.get('email', '')
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if email:
            queryset = queryset.filter(email__icontains=email)
        return queryset

class CustomUserCreateView(AjaxFormMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/form_usuario.html'
    template_name_ajax = 'accounts/form_usuario.html'
    success_url = reverse_lazy('accounts:lista_usuarios')

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuário criado com sucesso!')
        return response

class CustomUserDetailView(DetailView):
    model = User
    template_name = 'accounts/detalhes_usuario_modal.html'
    context_object_name = 'accounts'
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        if is_ajax(request):
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)

class CustomUserUpdateView(AjaxFormMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/form_usuario.html'
    template_name_ajax = 'accounts/form_usuario.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('accounts:lista_usuarios')

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuário atualizado com sucesso!')
        return response

class CustomUserDeleteView(DeleteView):
    model = User
    template_name = 'accounts/confirm_delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('accounts:lista_usuarios')

    def get_object(self, queryset=None):
        return get_object_or_404(User, id=self.kwargs.get('id'))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        if is_ajax(request):
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        email = self.object.email
        try:
            self.object.delete()

            if is_ajax(request):
                return JsonResponse({
                    'success': True,
                    'message': f'Usuário "{email}" excluído com sucesso!'
                })
            else:
                messages.success(request, f'Usuário "{email}" excluído com sucesso!')
                return redirect(self.success_url)

        except Exception as e:
            logger.error(f"Erro ao excluir usuário {email}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Erro ao excluir o usuário.'
            })
