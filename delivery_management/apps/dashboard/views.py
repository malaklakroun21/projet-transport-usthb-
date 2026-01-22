from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.expeditions.models import Expedition

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Access denied")

    expeditions = Expedition.objects.all()

    context = {
        'total_expeditions': expeditions.count(),
        'livrees': expeditions.filter(statut='livree').count(),
        'en_cours': expeditions.filter(statut='en_cours').count(),
        'creees': expeditions.filter(statut='cree').count(),
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def agent_dashboard(request):
    if request.user.role != 'agent':
        return HttpResponseForbidden("Access denied")

    expeditions = Expedition.objects.filter(created_by=request.user)

    context = {
        'total_expeditions': expeditions.count(),
        'livrees': expeditions.filter(statut='livree').count(),
        'en_cours': expeditions.filter(statut='en_cours').count(),
        'creees': expeditions.filter(statut='cree').count(),
    }

    return render(request, 'dashboard/agent_dashboard.html', context)
