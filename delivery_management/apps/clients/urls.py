from django.urls import path
from . import views

urlpatterns = [
    path('clients/', views.clients, name='clients'), 
    path('create-client/', views.createclient, name='create-client'),  
    path('update-client/<str:pk>/', views.updateclient, name='update-client'),
    path('delete-client/<str:pk>/', views.deleteclient, name='delete-client'),
    path('export-clients-csv/', views.export_clients, name='export-clients-csv'),
    
]