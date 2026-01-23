from django.forms import ModelForm 
from .models import Client

class ClientsForm(ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        exclude = ['created_at']