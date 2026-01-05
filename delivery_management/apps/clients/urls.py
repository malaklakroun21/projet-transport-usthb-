from django.urls import path
from . import views

urlpatterns = [
    path('', views.clients, name='clients'), 
    path('create-client/', views.createclient, name='create-client'),  
    path('update-client/<str:pk>/', views.updateclient, name='update-client'),
    path('delete-client/<str:pk>/', views.deleteclient, name='delete-client'),
]