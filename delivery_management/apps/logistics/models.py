import uuid
from decimal import Decimal
from django.db import models
from clients.models import Client

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



class Tour(models.Model):
    id_tour = models.DecimalField(max_digits=20, unique=True)
    id_driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    id_vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    tour_date = models.DateField()
    starting_hour = models.TimeField()
    finishing_hour = models.TimeField()
    kilometers = models.FloatField()
    duration = models.DurationField()
    status = models.CharField(max_length=30)
    comments = models.TextField(null=True, blank=True)



class Shipment(models.Model):
    tracking_number = models.CharField(max_length=30, unique=True, editable=False)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    id_destination = models.ForeignKey(Destination, on_delete=models.PROTECT)
    id_tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, blank=True)
    weight = models.FloatField()
    volume = models.FloatField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery_date = models.DateField()
    reel_delivery_date = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('CREATED', 'Créée'),
        ('PENDING', 'En attente'),
        ('IN_TRANSIT', 'En transit'),
        ('DELIVERED', 'Livrée'),
        ('FAILED', 'Échec'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CREATED'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

#calculate total price

    def calculate_total(self):
        return (
            self.Destination.id_zone.base_price +
            Decimal(self.weight) * self.ServiceType.weight_rate +
            Decimal(self.volume) * self.ServiceType.volume_rate
        )
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"EXP-{uuid.uuid4().hex[:8].upper()}"

        self.total_price = self.calculate_total()
        super().save(*args, **kwargs)


#I AM NOT SURE ABOUT THE RELATIONSHIP BETWEEN TOUR AND SHIPMENT

class TourShipment(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
