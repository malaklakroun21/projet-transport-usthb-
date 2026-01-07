from django.forms import ModelForm 
from .models import Clients

class ClientsForm(ModelForm):
    class Meta:
        model = Clients
        fields = '__all__'
        exclude = ['created_at']