

from django.urls import path 
from pages import views

urlpatterns = [
    path('', views.index, name='index'), 
    #path('error404/', views.error404, name='error404'),
    #path('error500/', views.error500, name='error500'),
]


