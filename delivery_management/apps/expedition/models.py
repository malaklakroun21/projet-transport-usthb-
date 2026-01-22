from django.db import models
from django.conf import settings
from clients.models import Client
from logistics.models import ServiceType, Destination, Vehicle, Driver
import uuid
import decimal


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
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expeditions'
    )
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
            decimal.Decimal(self.weight) * self.ServiceType.weight_rate +
            decimal.Decimal(self.volume) * self.ServiceType.volume_rate
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
