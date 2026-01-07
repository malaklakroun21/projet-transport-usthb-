from .models import Expedition
from django import forms


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Expedition
        fields = "__all__"