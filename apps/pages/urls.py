

from django.urls import path, re_path
from apps.pages import views

urlpatterns = [

    # The home page
    path('', views.index, name='pages'),

   
]
