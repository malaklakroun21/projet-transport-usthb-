from django.urls import path
from . import views

urlpatterns = [
    path('', views.incident_list, name='incident_list'),
    path('nouveau/', views.incident_create, name='incident_create'),
    path('<int:pk>/', views.incident_detail, name='incident_detail'),
    path('<int:pk>/status/', views.incident_update_status, name='incident_update_status'),
]
