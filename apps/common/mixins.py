class SuccessMessageMixin:
    """Adiciona mensagem de sucesso ao contexto da view"""
    success_message = None
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            from django.contrib import messages
            messages.success(self.request, self.success_message)
        return response 