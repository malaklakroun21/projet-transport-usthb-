from decimal import Decimal
import uuid
from django import forms
from django.db import models
from django.utils import timezone
from apps.clients.models import Client
from django.conf import settings


class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=50, blank=True)
    capacity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.immatriculation


class Driver(models.Model):
    id_driver = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Chauffeur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nom


class TypeService(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    weight_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    volume_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nom


class Zone(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nom


class Destination(models.Model):
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=20)
    pays = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.ville} ({self.pays})"


class Tour(models.Model):
    id_tour = models.AutoField(primary_key=True)
    id_driver = models.ForeignKey(Driver, on_delete=models.PROTECT, null=True, blank=True)
    id_vehicle = models.ForeignKey(Vehicule, on_delete=models.PROTECT, null=True, blank=True)
    tour_date = models.DateField(null=True, blank=True)
    starting_hour = models.TimeField(null=True, blank=True)
    finishing_hour = models.TimeField(null=True, blank=True)
    kilometers = models.FloatField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    status = models.CharField(max_length=30, default='pending')
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Tour {self.id_tour} - {self.tour_date}"


class Tournee(models.Model):
    date = models.DateField(default=timezone.now)
    chauffeur = models.ForeignKey('logistics.Chauffeur', on_delete=models.PROTECT)
    vehicule = models.ForeignKey('logistics.Vehicule', on_delete=models.PROTECT)

    def __str__(self):
        return f"Tournée {self.date}"


class Shipment(models.Model):
    tracking_number = models.CharField(max_length=30, unique=True, editable=False)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    id_service_type = models.ForeignKey(TypeService, on_delete=models.PROTECT, null=True, blank=True)
    id_destination = models.ForeignKey(Destination, on_delete=models.PROTECT, null=True, blank=True)
    id_tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    reel_delivery_date = models.DateField(null=True, blank=True)

    # Workflow: Enregistré → Transit → Tri → Livraison → [Livré | Échec]
    STATUS_CHOICES = [
        ('REGISTERED', 'Enregistré'),
        ('TRANSIT', 'En transit'),
        ('SORTING', 'Centre de tri'),
        ('OUT_FOR_DELIVERY', 'En cours de livraison'),
        ('DELIVERED', 'Livré'),
        ('FAILED', 'Échec de livraison'),
    ]
    
    # Workflow transitions allowed
    STATUS_WORKFLOW = {
        'REGISTERED': ['TRANSIT'],
        'TRANSIT': ['SORTING'],
        'SORTING': ['OUT_FOR_DELIVERY'],
        'OUT_FOR_DELIVERY': ['DELIVERED', 'FAILED'],
        'DELIVERED': [],
        'FAILED': ['OUT_FOR_DELIVERY'],  # Retry allowed
    }
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expeditions',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REGISTERED'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    class Meta:
        verbose_name = "Expédition"
        verbose_name_plural = "Expéditions"

    def __str__(self):
        return f"{self.tracking_number}"

    def calculate_total(self):
        if self.id_destination and self.id_service_type:
            # Prix de base depuis la zone de la destination
            base = 0
            if self.id_destination.zone:
                base = self.id_destination.zone.base_price or 0
            weight_rate = self.id_service_type.weight_rate or 0
            volume_rate = self.id_service_type.volume_rate or 0
            weight = self.weight or 0
            volume = self.volume or 0
            return Decimal(base) + Decimal(weight) * Decimal(weight_rate) + Decimal(volume) * Decimal(volume_rate)
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"EXP-{uuid.uuid4().hex[:8].upper()}"
        self.total_price = self.calculate_total()
        super().save(*args, **kwargs)
    
    def can_transition_to(self, new_status):
        """Check if transition to new_status is allowed"""
        allowed = self.STATUS_WORKFLOW.get(self.status, [])
        return new_status in allowed
    
    def get_next_statuses(self):
        """Get list of valid next statuses"""
        return self.STATUS_WORKFLOW.get(self.status, [])
    
    def get_status_progress(self):
        """Return progress percentage for timeline"""
        progress_map = {
            'REGISTERED': 0,
            'TRANSIT': 25,
            'SORTING': 50,
            'OUT_FOR_DELIVERY': 75,
            'DELIVERED': 100,
            'FAILED': 75,
        }
        return progress_map.get(self.status, 0)


class ShipmentStatusHistory(models.Model):
    """Track all status changes for timeline"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Shipment.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Historique de statut"
        verbose_name_plural = "Historiques de statuts"
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.get_status_display()} ({self.changed_at})"

