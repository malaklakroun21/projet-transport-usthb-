from django.shortcuts import render, redirect
from .models import Clients
from .forms import ClientsForm
from django.db.models import Q
from django.http import HttpResponse
import csv




# Create your views here.
def clients(request):
    query = request.GET.get('q')           # search query
    status = request.GET.get('status')     # filter dropdown

    clients = Clients.objects.all()

    # Apply search filter
    if query:
        clients = clients.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(address__icontains=query)
        )

    # Apply status filter
    if status and status != 'ALL':
        clients = clients.filter(client_type=status)

    context = {
        'clients': clients,
        'query': query,
        'status': status or 'ALL'
    }
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




def export_clients(request):
    # Create the HttpResponse object with CSV headers
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="clients.csv"'},
    )

    writer = csv.writer(response)
    # Write header row
    writer.writerow(['Code Client', 'Nom', 'Téléphone', 'Email', 'Adresse', 'Type', 'Solde'])

    # Write data rows
    clients = Clients.objects.all()
    for client in clients:
        writer.writerow([
            client.code_client,
            client.name,
            client.phone,
            client.email,
            client.address,
            client.client_type,
            client.balance
        ])

    return response
