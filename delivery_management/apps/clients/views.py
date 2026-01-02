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

