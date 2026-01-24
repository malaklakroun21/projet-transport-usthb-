from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django import forms
from decimal import Decimal

from apps.logistics.models import Shipment, TypeService, Destination, Tour
from apps.clients.models import Client


# Définition des formulaires pour chaque étape
class Step1Form(forms.Form):
    """Étape 1: Sélection client et type de service"""
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        label="Client",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    type_service = forms.ModelChoiceField(
        queryset=TypeService.objects.all(),
        label="Type de service",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class Step2Form(forms.Form):
    """Étape 2: Destination et dimensions"""
    destination = forms.ModelChoiceField(
        queryset=Destination.objects.all(),
        label="Destination",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Description du colis",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class Step3Form(forms.Form):
    """Étape 3: Poids, volume et tournée"""
    poids = forms.DecimalField(
        label="Poids (kg)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    volume = forms.DecimalField(
        label="Volume (m³)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    tour = forms.ModelChoiceField(
        queryset=Tour.objects.all(),
        label="Tournée",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class Step4Form(forms.Form):
    """Étape 4: Confirmation"""
    # Formulaire vide pour confirmation
    pass


STEP_FORMS = {
    1: Step1Form,
    2: Step2Form,
    3: Step3Form,
    4: Step4Form,
}

STEP_TITLES = {
    1: "Informations client",
    2: "Destination",
    3: "Dimensions et tournée",
    4: "Confirmation",
}


@login_required
def expedition_wizard(request):
    """Vue principale du wizard multi-étapes"""
    # Gérer le retour en arrière via GET param
    step_param = request.GET.get('step')
    if step_param:
        try:
            new_step = int(step_param)
            if 1 <= new_step <= 4:
                request.session['wizard_step'] = new_step
                return redirect('expedition:wizard')
        except ValueError:
            pass
    
    # Récupérer l'étape actuelle depuis la session
    current_step = request.session.get('wizard_step', 1)
    expedition_data = request.session.get('expedition_data', {})
    
    # Obtenir la classe de formulaire pour cette étape
    FormClass = STEP_FORMS.get(current_step, Step1Form)
    
    if request.method == 'POST':
        form = FormClass(request.POST)
        
        if form.is_valid():
            # Sauvegarder les données de l'étape actuelle
            if current_step == 1:
                client = form.cleaned_data['client']
                type_service = form.cleaned_data['type_service']
                expedition_data['client_id'] = client.id
                expedition_data['client_name'] = str(client)
                expedition_data['type_service_id'] = type_service.id
                expedition_data['type_service_name'] = str(type_service)
                request.session['expedition_data'] = expedition_data
                request.session['wizard_step'] = 2
                
            elif current_step == 2:
                destination = form.cleaned_data['destination']
                expedition_data['destination_id'] = destination.id
                expedition_data['destination_name'] = str(destination)
                expedition_data['description'] = form.cleaned_data.get('description', '')
                request.session['expedition_data'] = expedition_data
                request.session['wizard_step'] = 3
                
            elif current_step == 3:
                expedition_data['poids'] = str(form.cleaned_data['poids'])
                expedition_data['volume'] = str(form.cleaned_data['volume'])
                tour = form.cleaned_data.get('tour')
                if tour:
                    expedition_data['tour_id'] = tour.id_tour
                    expedition_data['tour_name'] = str(tour)
                # Calculer le montant
                expedition_data['montant_total'] = str(calculate_price(expedition_data))
                request.session['expedition_data'] = expedition_data
                request.session['wizard_step'] = 4
                
            elif current_step == 4:
                # Création de l'expédition
                shipment = Shipment()
                
                if expedition_data.get('client_id'):
                    shipment.id_client = Client.objects.filter(id=expedition_data['client_id']).first()
                if expedition_data.get('type_service_id'):
                    shipment.id_service_type = TypeService.objects.filter(id=expedition_data['type_service_id']).first()
                if expedition_data.get('destination_id'):
                    shipment.id_destination = Destination.objects.filter(id=expedition_data['destination_id']).first()
                if expedition_data.get('tour_id'):
                    shipment.id_tour = Tour.objects.filter(id_tour=expedition_data['tour_id']).first()
                
                shipment.weight = float(expedition_data.get('poids') or 0)
                shipment.volume = float(expedition_data.get('volume') or 0)
                shipment.description = expedition_data.get('description', '')
                shipment.created_by = request.user
                
                shipment.save()
                
                # Nettoyer la session
                request.session.pop('wizard_step', None)
                request.session.pop('expedition_data', None)
                
                return redirect('expedition:success', pk=shipment.pk)
            
            return redirect('expedition:wizard')
    else:
        # Pré-remplir le formulaire avec les données existantes
        initial = {}
        if current_step == 1:
            if expedition_data.get('client_id'):
                initial['client'] = expedition_data['client_id']
            if expedition_data.get('type_service_id'):
                initial['type_service'] = expedition_data['type_service_id']
        elif current_step == 2:
            if expedition_data.get('destination_id'):
                initial['destination'] = expedition_data['destination_id']
            if expedition_data.get('description'):
                initial['description'] = expedition_data['description']
        elif current_step == 3:
            if expedition_data.get('poids'):
                initial['poids'] = expedition_data['poids']
            if expedition_data.get('volume'):
                initial['volume'] = expedition_data['volume']
            if expedition_data.get('tour_id'):
                initial['tour'] = expedition_data['tour_id']
        
        form = FormClass(initial=initial)
    
    # Préparer le contexte
    context = {
        'current_step': current_step,
        'total_steps': 4,
        'expedition_data': expedition_data,
        'step_titles': STEP_TITLES,
        'form': form,
    }
    
    return render(request, 'expedition/wizard.html', context)


def calculate_price(expedition_data):
    """Calcule le prix estimé basé sur les données du wizard"""
    price = Decimal('0.00')
    
    if expedition_data.get('destination_id'):
        destination = Destination.objects.filter(id=expedition_data['destination_id']).first()
        if destination and destination.zone:
            price += destination.zone.base_price or Decimal('0')
    
    if expedition_data.get('type_service_id'):
        service_type = TypeService.objects.filter(id=expedition_data['type_service_id']).first()
        if service_type:
            poids = Decimal(expedition_data.get('poids') or '0')
            volume = Decimal(expedition_data.get('volume') or '0')
            price += poids * (service_type.weight_rate or Decimal('0'))
            price += volume * (service_type.volume_rate or Decimal('0'))
    
    return price


@login_required
def calculate_price_ajax(request):
    """API pour calculer le prix en temps réel"""
    expedition_data = {
        'destination_id': request.GET.get('destination_id'),
        'type_service_id': request.GET.get('type_service_id'),
        'poids': request.GET.get('poids'),
        'volume': request.GET.get('volume'),
    }
    
    price = calculate_price(expedition_data)
    return JsonResponse({'success': True, 'montant': float(price)})


@login_required
def expedition_success(request, pk):
    """Page de succès après création"""
    shipment = get_object_or_404(Shipment, pk=pk)
    return render(request, 'expedition/success.html', {'shipment': shipment})


@login_required
def expedition_reset(request):
    """Réinitialiser le wizard"""
    request.session.pop('wizard_step', None)
    request.session.pop('wizard_data', None)
    return redirect('expedition:wizard')
