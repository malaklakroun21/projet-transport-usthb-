from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.logistics.models import Shipment

@login_required
def admin_dashboard(request):
    # Permettre l'accès à tous les utilisateurs authentifiés
    expeditions = Shipment.objects.all()

    context = {
        'total_expeditions': expeditions.count(),
        'livrees': expeditions.filter(status='LIVREE').count(),
        'en_cours': expeditions.filter(status='EN_COURS').count(),
        'creees': expeditions.filter(status='EN_ATTENTE').count(),
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def agent_dashboard(request):
    if request.user.role != 'agent':
        return HttpResponseForbidden("Access denied")

    # Note: Le modèle Shipment n'a pas de champ created_by pour l'instant
    # Afficher toutes les expéditions pour les agents
    expeditions = Shipment.objects.all()

    context = {
        'total_expeditions': expeditions.count(),
        'livrees': expeditions.filter(status='LIVREE').count(),
        'en_cours': expeditions.filter(status='EN_COURS').count(),
        'creees': expeditions.filter(status='EN_ATTENTE').count(),
    }

    return render(request, 'dashboard/agent_dashboard.html', context)
