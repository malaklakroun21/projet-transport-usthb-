from django import forms
from .models import Reclamation, ReclamationComment, ReclamationDocument, ReclamationTask
from apps.clients.models import Client
from apps.logistics.models import Shipment
from apps.facturation.models import Invoice
from django.contrib.auth import get_user_model

User = get_user_model()


class ReclamationForm(forms.ModelForm):
    """Formulaire de création/modification de réclamation"""
    
    class Meta:
        model = Reclamation
        fields = [
            'client', 'type_reclamation', 'description', 
            'shipments', 'invoice', 'priority', 'assigned_to'
        ]
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'type_reclamation': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez la réclamation en détail...'
            }),
            'shipments': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 4
            }),
            'invoice': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les expéditions par client si un client est sélectionné
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['shipments'].queryset = Shipment.objects.filter(client_id=client_id)
                self.fields['invoice'].queryset = Invoice.objects.filter(client_id=client_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['shipments'].queryset = Shipment.objects.filter(client=self.instance.client)
            self.fields['invoice'].queryset = Invoice.objects.filter(client=self.instance.client)
        
        # Agents assignables (tous les utilisateurs staff)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
        self.fields['assigned_to'].required = False
        self.fields['invoice'].required = False


class ReclamationStatusForm(forms.ModelForm):
    """Formulaire pour changer le statut d'une réclamation"""
    
    class Meta:
        model = Reclamation
        fields = ['status', 'resolution']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'resolution': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez la résolution...'
            }),
        }


class ReclamationCommentForm(forms.ModelForm):
    """Formulaire pour ajouter un commentaire"""
    
    class Meta:
        model = ReclamationComment
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ajouter un commentaire...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ReclamationDocumentForm(forms.ModelForm):
    """Formulaire pour ajouter un document"""
    
    class Meta:
        model = ReclamationDocument
        fields = ['file', 'name']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du document'
            }),
        }


class ReclamationTaskForm(forms.ModelForm):
    """Formulaire pour créer une tâche"""
    
    class Meta:
        model = ReclamationTask
        fields = ['title', 'description', 'assigned_to', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la tâche'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Description (optionnel)'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)


class ReclamationFilterForm(forms.Form):
    """Formulaire de filtrage des réclamations"""
    
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + list(Reclamation.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    type_reclamation = forms.ChoiceField(
        choices=[('', 'Tous les types')] + list(Reclamation.TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'Toutes les priorités')] + list(Reclamation.PRIORITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        empty_label="Tous les clients",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher...'
        })
    )
