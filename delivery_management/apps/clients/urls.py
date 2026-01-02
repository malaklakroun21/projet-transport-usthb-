from django.urls import path
from .views import client_dashboard, client_create

urlpatterns = [
    path("clients/", client_dashboard, name="client_dashboard"),
    path("create/", client_create, name="client_create"),
]
