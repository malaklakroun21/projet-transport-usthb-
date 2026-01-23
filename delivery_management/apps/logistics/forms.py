from .models import Shipment
from django import forms


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = "__all__"
from django.forms import ModelForm 
from .models import Driver
from .models import Vehicle 
from .models import Destination
from .models import ServiceType
from .models import Zone

class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = '__all__'
        exclude = ['created_at']



class VehicleForm(ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
        exclude = ['created_at']        




class DestinationForm(ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'
        exclude = ['created_at']        




class ServiceTypeForm(ModelForm):
    class Meta:
        model = ServiceType
        fields = '__all__'
        exclude = ['created_at']        



class zoneForm(ModelForm):
    class Meta:
        model = Zone
        fields = '__all__'
        exclude = ['created_at']        
