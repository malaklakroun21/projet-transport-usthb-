from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import uuid

from .forms import (
    Step1ClientForm,
    Step2ServiceDestinationForm,
    Step3ColisDetailsForm,
    Step4AffectationForm
)
from apps.clients.models import Client
from apps.logistics.models import ServiceType, Destination, Tour, Shipment


# Tarifs pour le calcul du montant
PRIX_PAR_KG = 5.0  # Prix par kg
PRIX_PAR_M3 = 20.0  # Prix par m³
FRAIS_BASE = 10.0  # Frais de base


def calculer_montant(poids, volume, type_service=None):
    """Calcule le montant total de l'expédition"""
    montant = FRAIS_BASE + (poids * PRIX_PAR_KG) + (volume * PRIX_PAR_M3)
    return round(montant, 2)


def expedition_wizard(request):
    """Vue principale du formulaire multi-étapes"""
    
    # Initialiser la session si nécessaire
    if 'expedition_data' not in request.session:
        request.session['expedition_data'] = {}
    
    # Récupérer l'étape actuelle (1 par défaut)
    current_step = int(request.GET.get('step', 1))
    
    # Récupérer les données de session
    expedition_data = request.session.get('expedition_data', {})
    
    if request.method == 'POST':
        if current_step == 1:
            form = Step1ClientForm(request.POST)
            if form.is_valid():
                expedition_data['client_id'] = form.cleaned_data['client'].id
                expedition_data['client_name'] = str(form.cleaned_data['client'])
                request.session['expedition_data'] = expedition_data
                return redirect('expedition:wizard') + '?step=2'
        
        elif current_step == 2:
            form = Step2ServiceDestinationForm(request.POST)
            if form.is_valid():
                expedition_data['type_service_id'] = form.cleaned_data['type_service'].id
                expedition_data['type_service_name'] = str(form.cleaned_data['type_service'])
                expedition_data['destination_id'] = form.cleaned_data['destination'].id
                expedition_data['destination_name'] = str(form.cleaned_data['destination'])
                request.session['expedition_data'] = expedition_data
                return redirect('expedition:wizard') + '?step=3'
        
        elif current_step == 3:
            form = Step3ColisDetailsForm(request.POST)
            if form.is_valid():
                poids = form.cleaned_data['poids']
                volume = form.cleaned_data['volume']
                
                expedition_data['poids'] = poids
                expedition_data['volume'] = volume
                expedition_data['description'] = form.cleaned_data['description']
                expedition_data['date_livraison_estimee'] = str(form.cleaned_data['date_livraison_estimee'])
                expedition_data['montant_total'] = calculer_montant(poids, volume)
                request.session['expedition_data'] = expedition_data
                return redirect('expedition:wizard') + '?step=4'
        
        elif current_step == 4:
            form = Step4AffectationForm(request.POST)
            if form.is_valid():
                # Créer l'expédition
                tournee = form.cleaned_data.get('tournee')
                
                expedition = Shipment.objects.create(
                    client_id=expedition_data['client_id'],
                    service_type_id=expedition_data['type_service_id'],
                    destination_id=expedition_data['destination_id'],
                    weight=expedition_data['poids'],
                    volume=expedition_data['volume'],
                    description=expedition_data['description'],
                    estimated_delivery_date=expedition_data['date_livraison_estimee'],
                    total_price=expedition_data['montant_total'],
                    tour=tournee,
                    status='EN_ATTENTE' if not tournee else 'EN_COURS'
                )
                
                # Nettoyer la session
                del request.session['expedition_data']
                
                messages.success(request, f"Expédition {expedition.tracking_number} créée avec succès!")
                return redirect('expedition:success', pk=expedition.pk)
    
    else:
        # GET request - afficher le formulaire approprié
        if current_step == 1:
            form = Step1ClientForm()
        elif current_step == 2:
            if 'client_id' not in expedition_data:
                return redirect('expedition:wizard') + '?step=1'
            form = Step2ServiceDestinationForm()
        elif current_step == 3:
            if 'destination_id' not in expedition_data:
                return redirect('expedition:wizard') + '?step=2'
            form = Step3ColisDetailsForm()
        elif current_step == 4:
            if 'poids' not in expedition_data:
                return redirect('expedition:wizard') + '?step=3'
            form = Step4AffectationForm()
        else:
            return redirect('expedition:wizard') + '?step=1'
    
    context = {
        'form': form,
        'current_step': current_step,
        'total_steps': 4,
        'expedition_data': expedition_data,
        'step_titles': {
            1: 'Sélection du client',
            2: 'Service et destination',
            3: 'Détails du colis',
            4: 'Affectation à une tournée'
        }
    }
    
    return render(request, 'expedition/wizard.html', context)


def calculate_price_ajax(request):
    """API pour calculer le prix en temps réel"""
    if request.method == 'GET':
        try:
            poids = float(request.GET.get('poids', 0))
            volume = float(request.GET.get('volume', 0))
            montant = calculer_montant(poids, volume)
            return JsonResponse({'montant': montant, 'success': True})
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Valeurs invalides', 'success': False})
    return JsonResponse({'error': 'Méthode non autorisée', 'success': False})


def expedition_success(request, pk):
    """Page de confirmation après création"""
    expedition = Shipment.objects.get(pk=pk)
    return render(request, 'expedition/success.html', {'expedition': expedition})


def expedition_reset(request):
    """Réinitialiser le formulaire wizard"""
    if 'expedition_data' in request.session:
        del request.session['expedition_data']
    return redirect('expedition:wizard')
