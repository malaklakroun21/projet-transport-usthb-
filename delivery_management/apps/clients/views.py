from django.shortcuts import render, redirect
from .models import Clients
from .forms import ClientsForm




# Create your views here.
def clients(request):
    clients = Clients.objects.all()
    context = {'clients': clients}
    return render(request, 'clients/clients.html', context)

def createclient(request):
    form = ClientsForm()

    if request.method == 'POST':
        form = ClientsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clients')

    context = {'form': form}
    return render(request, 'clients/clients-form.html', context)


def updateclient(request, pk):
    client = Clients.objects.get(id=pk)
    form = ClientsForm(instance=client)

    if request.method == 'POST':
        form = ClientsForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('clients')

    context = {'form': form}
    return render(request, 'clients/clients-form.html', context)    





def deleteclient(request, pk):   
    client = Clients.objects.get(id=pk)
    if request.method == 'POST':
        client.delete()
        return redirect('clients')
    context = {'client': client}
    return render(request, 'clients/clients-delete.html', context)





