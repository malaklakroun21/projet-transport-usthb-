from decimal import Decimal
import uuid
from django import forms
from django.db import models
from django.utils import timezone
from apps.clients.models import Client

# ---------------- DRIVERS ----------------
class Driver(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ---------------- VEHICLES ----------------
class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50)
    capacity = models.FloatField()
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.plate_number


# ---------------- ZONES ----------------
class Zone(models.Model):
    name = models.CharField(max_length=50)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name


# ---------------- DESTINATIONS ----------------
class Destination(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.city}, {self.country}"




# ---------------- SERVICE TYPES ----------------
class ServiceType(models.Model):
    name = models.CharField(max_length=50)
    weight_rate = models.DecimalField(max_digits=8, decimal_places=2)
    volume_rate = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name


# ---------------- TOURS ----------------
class Tour(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    tour_date = models.DateField()
    starting_hour = models.TimeField()
    finishing_hour = models.TimeField()
    kilometers = models.FloatField()
    duration = models.DurationField()
    status = models.CharField(max_length=30)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Tour {self.id} - {self.tour_date}"

# ---------------- SHIPMENTS ----------------
class Shipment(models.Model):
    tracking_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT)
    tour = models.ForeignKey(
        Tour,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    weight = models.FloatField()
    volume = models.FloatField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery_date = models.DateField()
    real_delivery_date = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_COURS', 'En cours'),
        ('LIVREE', 'Livrée'),
        ('ANNULEE', 'Annulée'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EN_ATTENTE'
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    def calculate_total(self):
        return (
            self.destination.zone.base_price +
            Decimal(self.weight) * self.service_type.weight_rate +
            Decimal(self.volume) * self.service_type.volume_rate
        )

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"EXP-{uuid.uuid4().hex[:8].upper()}"

        self.total_price = self.calculate_total()
        super().save(*args, **kwargs)
