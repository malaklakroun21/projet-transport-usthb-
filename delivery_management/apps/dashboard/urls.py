from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='home'),  # Homepage = dashboard
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
]
