from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
]
