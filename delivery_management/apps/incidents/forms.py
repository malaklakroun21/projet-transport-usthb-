from django import forms
from .models import Incident, IncidentDocument, IncidentComment


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['incident_type', 'shipment', 'tour', 'priority', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        shipment = cleaned_data.get('shipment')
        tour = cleaned_data.get('tour')
        if not shipment and not tour:
            raise forms.ValidationError(
                "Vous devez sélectionner une expédition ou une tournée."
            )
        return cleaned_data


class IncidentStatusForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['status', 'resolution', 'assigned_to']
        widgets = {
            'resolution': forms.Textarea(attrs={'rows': 3}),
        }


class IncidentDocumentForm(forms.ModelForm):
    class Meta:
        model = IncidentDocument
        fields = ['file', 'description']


class IncidentCommentForm(forms.ModelForm):
    class Meta:
        model = IncidentComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2}),
        }
