from django import forms
from .models import Tour, TourExpedition
from apps.logistics.models import Driver, Vehicule, Shipment


class TourCreateForm(forms.ModelForm):
    """Formulaire de création de tournée - seulement les ressources"""
    class Meta:
        model = Tour
        fields = ['id_driver', 'id_vehicle', 'tour_date', 'starting_hour', 'comments']
        widgets = {
            'tour_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'starting_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes optionnelles...'}),
            'id_driver': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'id_vehicle': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
        labels = {
            'id_driver': 'Chauffeur',
            'id_vehicle': 'Véhicule',
            'tour_date': 'Date de la tournée',
            'starting_hour': 'Heure de départ',
            'comments': 'Notes',
        }


class TourForm(forms.ModelForm):
    """Formulaire complet de modification de tournée"""
    class Meta:
        model = Tour
        fields = [
            'id_driver', 'id_vehicle', 'tour_date', 'starting_hour', 'finishing_hour',
            'kilometers', 'fuel_consumption', 'status', 'comments',
            'has_delay', 'delay_minutes', 'has_technical_issue', 'technical_issue_description'
        ]
        widgets = {
            'tour_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'starting_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'finishing_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'kilometers': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'fuel_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'delay_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'technical_issue_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'id_driver': forms.Select(attrs={'class': 'form-control'}),
            'id_vehicle': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class TourCompleteForm(forms.Form):
    """Formulaire pour terminer une tournée"""
    kilometers = forms.FloatField(
        label="Kilométrage parcouru (km)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    fuel_consumption = forms.FloatField(
        label="Consommation carburant (L)",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    has_delay = forms.BooleanField(
        label="Retard signalé",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    delay_minutes = forms.IntegerField(
        label="Minutes de retard",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    has_technical_issue = forms.BooleanField(
        label="Problème technique rencontré",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    technical_issue_description = forms.CharField(
        label="Description du problème",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    comments = forms.CharField(
        label="Commentaires",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class AddExpeditionForm(forms.Form):
    """Formulaire pour ajouter une expédition à une tournée"""
    expedition = forms.ModelChoiceField(
        queryset=Shipment.objects.filter(status__in=['CREATED', 'PENDING']),
        label="Expédition",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, tour=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclure les expéditions déjà assignées à cette tournée
        if tour:
            assigned_ids = tour.tour_expeditions.values_list('expedition_id', flat=True)
            self.fields['expedition'].queryset = Shipment.objects.filter(
                status__in=['CREATED', 'PENDING']
            ).exclude(id__in=assigned_ids)
