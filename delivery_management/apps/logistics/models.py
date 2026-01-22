import uuid
from decimal import Decimal
from django.db import models
from clients.models import Client
from delivery_management.delivery_management import settings

class Driver(models.Model):
    id_driver = models.DecimalField(max_digits=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    available = models.BooleanField(default=True)


class Vehicle(models.Model):
    id_vehicle = models.DecimalField(max_digits=20, unique=True)
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50)
    capacity = models.FloatField()
    status = models.CharField(max_length=30)


class Zone(models.Model):
    id_zone = models.DecimalField(max_digits=20, unique=True)
    name_zone = models.CharField(max_length=50)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)


class Destination(models.Model):
    id_destination = models.DecimalField(max_digits=20, unique=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    id_zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=20)


class ServiceType(models.Model):
    id_service_type = models.DecimalField(max_digits=20, unique=True)
    name_servicetype = models.CharField(max_length=50)
    weight_rate = models.DecimalField(max_digits=8, decimal_places=2)
    volume_rate = models.DecimalField(max_digits=8, decimal_places=2)


class Pricing(models.Model):
    id_service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    id_destination = models.ForeignKey(Destination, on_delete=models.CASCADE)

