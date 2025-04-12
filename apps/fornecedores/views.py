from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from .models import Fornecedor
from .forms import FornecedorForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class FornecedorListView(ListView):
    model = Fornecedor
    template_name = 'fornecedores/lista.html'
    context_object_name = 'fornecedores'

class AjaxFormMixin:
    """
    Mixin que permite o suporte AJAX para CreateView, UpdateView e DeleteView.
    Detecta se a requisição é AJAX (via modal) e retorna o template adequado.
    """

    template_name_ajax = None  # Define isso na sua view!

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Só tenta buscar objeto se a view de fato edita ou deleta (tem slug/pk)
            try:
                self.object = self.get_object()
            except AttributeError:
                self.object = None

            context = self.get_context_data()
            return render(request, self.template_name_ajax, context)

        return super().get(request, *args, **kwargs)


class FornecedorCreateView(AjaxFormMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    success_url = reverse_lazy('fornecedores:lista_fornecedores')
    template_name = 'fornecedores/fornecedor_form.html'        
    template_name_ajax = 'fornecedores/form_modal.html' 
    
class FornecedorUpdateView(AjaxFormMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    success_url = reverse_lazy('fornecedores:lista_fornecedores')
    template_name = 'fornecedores/fornecedor_form.html'
    template_name_ajax = 'fornecedores/form_modal.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class FornecedorDeleteView(DeleteView):
    model = Fornecedor
    success_url = reverse_lazy('fornecedores:lista_fornecedores')
    template_name = 'fornecedores/confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, self.template_name, context)

        return super().get(request, *args, **kwargs)


