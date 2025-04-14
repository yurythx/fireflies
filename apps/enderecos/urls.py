# apps/enderecos/urls.py

from django.urls import path
from .views import CidadesPorEstadoView

urlpatterns = [
    path('cidades-por-estado/<int:estado_id>/', CidadesPorEstadoView.as_view(), name='cidades_por_estado'),
]
