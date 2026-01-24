from django import forms
from django.forms import ModelForm
from .models import Shipment, Driver, Vehicule, Destination, TypeService, Zone


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = "__all__"


class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = '__all__'


class VehiculeForm(ModelForm):
    class Meta:
        model = Vehicule
        fields = '__all__'


class DestinationForm(ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'


class TypeServiceForm(ModelForm):
    class Meta:
        model = TypeService
        fields = '__all__'


class ZoneForm(ModelForm):
    class Meta:
        model = Zone
        fields = '__all__'
