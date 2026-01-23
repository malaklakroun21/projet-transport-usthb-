from django.db import models
from django.conf import settings
from apps.logistics.models import Shipment, Tour


class Incident(models.Model):
    """Modèle pour gérer les incidents lors des expéditions ou tournées"""
    
    TYPE_CHOICES = [
        ('retard', 'Retard'),
        ('perte', 'Perte'),
        ('endommagement', 'Endommagement'),
        ('technique', 'Problème technique'),
        ('autre', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
    ]
    
    PRIORITY_CHOICES = [
        ('basse', 'Basse'),
        ('moyenne', 'Moyenne'),
        ('haute', 'Haute'),
        ('critique', 'Critique'),
    ]
    
    shipment = models.ForeignKey(
        Shipment, 
        on_delete=models.CASCADE, 
        related_name='incidents',
        null=True, 
        blank=True,
        verbose_name='Expédition'
    )
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='incidents',
        null=True, 
        blank=True,
        verbose_name='Tournée'
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_incidents',
        verbose_name='Signalé par'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        verbose_name='Assigné à'
    )
    
    incident_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES,
        verbose_name='Type d\'incident'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='ouvert',
        verbose_name='Statut'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='moyenne',
        verbose_name='Priorité'
    )
    description = models.TextField(verbose_name='Description')
    resolution = models.TextField(blank=True, null=True, verbose_name='Résolution')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='Date de résolution')
    
    alert_sent = models.BooleanField(default=False, verbose_name='Alerte envoyée')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'
    
    def __str__(self):
        return f"INC-{self.pk} - {self.get_incident_type_display()}"


class IncidentDocument(models.Model):
    """Documents/photos attachés à un incident"""
    
    incident = models.ForeignKey(
        Incident, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    file = models.FileField(upload_to='incidents/documents/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Document pour {self.incident}"


class IncidentComment(models.Model):
    """Commentaires sur un incident"""
    
    incident = models.ForeignKey(
        Incident, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Commentaire de {self.author} sur {self.incident}"
