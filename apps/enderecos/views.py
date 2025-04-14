from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .models import Estado  # Certifique-se de que o modelo Estado está no mesmo app ou ajuste o import


class CidadesPorEstadoView(View):
    def get(self, request, estado_id):
        estado = get_object_or_404(Estado, id=estado_id)
        cidades = estado.cidades.all().values('id', 'nome')
        return JsonResponse({'cidades': list(cidades)})