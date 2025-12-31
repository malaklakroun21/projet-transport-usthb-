from django.shortcuts import render, redirect
from .models import Clients

# Create your views here.
def clients(request):
    clients = Clients.objects.all()
    context = {'clients': clients}
    return render(request, 'clients/clients.html', context)