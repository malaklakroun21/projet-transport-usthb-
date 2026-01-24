from django.db import models
from django.utils import timezone


class Tour(models.Model):
    """Modèle de tournée pour regrouper les expéditions"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    id_tour = models.AutoField(primary_key=True)
    id_driver = models.ForeignKey(
        'logistics.Driver', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        verbose_name="Chauffeur",
        related_name="tours"
    )
    id_vehicle = models.ForeignKey(
        'logistics.Vehicule', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        verbose_name="Véhicule",
        related_name="tours"
    )
    tour_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Date de tournée",
        default=timezone.now
    )
    starting_hour = models.TimeField(null=True, blank=True, verbose_name="Heure de départ")
    finishing_hour = models.TimeField(null=True, blank=True, verbose_name="Heure d'arrivée")
    
    # Données du trajet
    kilometers = models.FloatField(null=True, blank=True, default=0, verbose_name="Kilométrage")
    duration = models.DurationField(null=True, blank=True, verbose_name="Durée")
    fuel_consumption = models.FloatField(null=True, blank=True, default=0, verbose_name="Consommation carburant (L)")
    
    status = models.CharField(
        max_length=30, 
        choices=STATUS_CHOICES, 
        default='pending', 
        verbose_name="Statut"
    )
    comments = models.TextField(null=True, blank=True, verbose_name="Commentaires")
    
    # Incidents et retards
    has_delay = models.BooleanField(default=False, verbose_name="Retard")
    delay_minutes = models.IntegerField(null=True, blank=True, default=0, verbose_name="Minutes de retard")
    has_technical_issue = models.BooleanField(default=False, verbose_name="Problème technique")
    technical_issue_description = models.TextField(null=True, blank=True, verbose_name="Description du problème")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tournée"
        verbose_name_plural = "Tournées"
        ordering = ['-tour_date', '-created_at']

    def __str__(self):
        driver_name = f"{self.id_driver}" if self.id_driver else "Non assigné"
        date_str = self.tour_date.strftime('%d/%m/%Y') if self.tour_date else "Sans date"
        return f"Tournée #{self.id_tour} - {date_str} ({driver_name})"
    
    @property
    def expeditions(self):
        """Retourne les expéditions liées via TourExpedition"""
        from apps.logistics.models import Shipment
        expedition_ids = self.tour_expeditions.values_list('expedition_id', flat=True)
        return Shipment.objects.filter(id__in=expedition_ids)
    
    @property
    def expedition_count(self):
        """Nombre d'expéditions dans cette tournée"""
        return self.tour_expeditions.count()
    
    @property
    def delivered_count(self):
        """Nombre d'expéditions livrées"""
        return self.tour_expeditions.filter(delivered=True).count()
    
    @property
    def total_weight(self):
        """Poids total des expéditions"""
        return sum(te.expedition.weight or 0 for te in self.tour_expeditions.select_related('expedition').all())
    
    @property
    def total_volume(self):
        """Volume total des expéditions"""
        return sum(te.expedition.volume or 0 for te in self.tour_expeditions.select_related('expedition').all())


class TourExpedition(models.Model):
    """Relation entre tournée et expédition avec ordre de livraison"""
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='tour_expeditions'
    )
    expedition = models.ForeignKey(
        'logistics.Shipment',
        on_delete=models.CASCADE,
        related_name='tour_assignments'
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre de livraison")
    delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Expédition de tournée"
        verbose_name_plural = "Expéditions de tournée"
        ordering = ['order']
        unique_together = ['tour', 'expedition']

    def __str__(self):
        return f"{self.tour} - {self.expedition}"
