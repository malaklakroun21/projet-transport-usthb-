from django.urls import path
from . import views

urlpatterns = [
    path('', views.reclamation_list, name='reclamation_list'),
    path('nouveau/', views.reclamation_create, name='reclamation_create'),
    path('<int:pk>/', views.reclamation_detail, name='reclamation_detail'),
    path('<int:pk>/modifier/', views.reclamation_edit, name='reclamation_edit'),
    path('<int:pk>/status/', views.reclamation_update_status, name='reclamation_update_status'),
    path('tache/<int:pk>/status/', views.task_update_status, name='task_update_status'),
    path('api/client-shipments/', views.get_client_shipments, name='client_shipments'),
]
