from django.urls import path
from .views import (
  CidadesPorEstadoView
)


app_name = 'enderecos'  # Certifique-se de que este app está registrado com o namespace correto

urlpatterns = [
    path('cidades_por_estado/<int:estado_id>/', CidadesPorEstadoView.as_view(), name='cidades_por_estado'),
    # Outros caminhos
]