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
import json
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt
from .models import Client


def client_dashboard(request):
    clients = Client.objects.all()

    data = []
    for client in clients:
        data.append({
            "id": client.id,
            "num_client": client.code_client,
            "nom": client.name,
            "email": client.email,
            "telephone": client.phone,
            "addresse": client.address,
            "type": client.client_type,
            "solde": float(client.balance),
            "created_at": localtime(client.created_at).isoformat(),
        })

    return JsonResponse(data, safe=False)


@csrf_exempt
def client_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        balance = data.get("solde")
        if balance in ("", None):
            balance = 0

        Client.objects.create(
            code_client=data.get("num_client"),
            name=data.get("nom"),
            email=data.get("email"),
            phone=data.get("telephone"),
            address=data.get("addresse"),
            client_type=data.get("type"),
            balance=balance
        )

        return JsonResponse(
            {"message": "Client créé avec succès"},
            status=201
        )

    except IntegrityError:
        return JsonResponse(
            {"error": "Numéro de client ou email déjà existant"},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )

