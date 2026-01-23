from django import forms
from apps.clients.models import Client
from apps.logistics.models import TypeService, Destination, Tournee


class Step1ClientForm(forms.Form):
    """Étape 1: Sélection du client"""
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        label="Client",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'client-select'
        }),
        empty_label="-- Sélectionnez un client --"
    )


class Step2ServiceDestinationForm(forms.Form):
    """Étape 2: Service et Destination"""
    type_service = forms.ModelChoiceField(
        queryset=TypeService.objects.all(),
        label="Type de service",
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        empty_label="-- Sélectionnez un service --"
    )
    
    destination = forms.ModelChoiceField(
        queryset=Destination.objects.all(),
        label="Destination",
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        empty_label="-- Sélectionnez une destination --"
    )


class Step3ColisDetailsForm(forms.Form):
    """Étape 3: Détails du colis (poids, volume, description)"""
    poids = forms.FloatField(
        label="Poids (kg)",
        min_value=0.1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'Ex: 2.5'
        })
    )
    
    volume = forms.FloatField(
        label="Volume (m³)",
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Ex: 0.5'
        })
    )
    
    description = forms.CharField(
        label="Description du colis",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Décrivez le contenu du colis...'
        })
    )
    
    date_livraison_estimee = forms.DateField(
        label="Date de livraison estimée",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class Step4AffectationForm(forms.Form):
    """Étape 4: Affectation à une tournée"""
    tournee = forms.ModelChoiceField(
        queryset=Tournee.objects.all(),
        label="Tournée",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        empty_label="-- Aucune tournée (affecter plus tard) --"
    )
