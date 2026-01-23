from django.db import models
from django.conf import settings
from apps.clients.models import Client
from apps.logistics.models import Shipment
from apps.facturation.models import Invoice


class Reclamation(models.Model):
    """Modèle pour gérer les réclamations clients"""
    
    # Types de réclamation
    TYPE_CHOICES = [
        ('retard', 'Retard de livraison'),
        ('colis_endommage', 'Colis endommagé'),
        ('colis_perdu', 'Colis perdu'),
        ('erreur_facturation', 'Erreur de facturation'),
        ('service_client', 'Service client'),
        ('autre', 'Autre'),
    ]
    
    # Statuts de la réclamation
    STATUS_CHOICES = [
        ('en_cours', 'En cours'),
        ('resolue', 'Résolue'),
        ('annulee', 'Annulée'),
    ]
    
    # Priorités
    PRIORITY_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    # Informations de base
    reference = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name='reclamations'
    )
    type_reclamation = models.CharField(
        max_length=30, 
        choices=TYPE_CHOICES,
        verbose_name="Nature de la réclamation"
    )
    description = models.TextField(verbose_name="Description détaillée")
    
    # Liens optionnels
    shipments = models.ManyToManyField(
        Shipment, 
        blank=True, 
        related_name='reclamations',
        verbose_name="Colis concernés"
    )
    invoice = models.ForeignKey(
        Invoice, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reclamations',
        verbose_name="Facture concernée"
    )
    
    # Statut et priorité
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='en_cours'
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='normale'
    )
    
    # Attribution
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reclamations_created',
        verbose_name="Créée par"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reclamations_assigned',
        verbose_name="Agent responsable"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Résolution
    resolution = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Description de la résolution"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Réclamation"
        verbose_name_plural = "Réclamations"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            import uuid
            from django.utils import timezone
            year = timezone.now().year
            self.reference = f"REC-{year}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.client.name}"
    
    @property
    def resolution_time(self):
        """Calcule le délai de résolution en jours"""
        if self.resolved_at and self.created_at:
            delta = self.resolved_at - self.created_at
            return delta.days
        return None


class ReclamationComment(models.Model):
    """Commentaires et suivi des réclamations"""
    reclamation = models.ForeignKey(
        Reclamation, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    content = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(
        default=False, 
        verbose_name="Note interne",
        help_text="Les notes internes ne sont pas visibles par le client"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commentaire de {self.author} sur {self.reclamation.reference}"


class ReclamationDocument(models.Model):
    """Documents attachés aux réclamations"""
    reclamation = models.ForeignKey(
        Reclamation, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    file = models.FileField(upload_to='reclamations/documents/')
    name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ReclamationTask(models.Model):
    """Tâches assignées aux agents pour traiter les réclamations"""
    
    STATUS_CHOICES = [
        ('a_faire', 'À faire'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ]
    
    reclamation = models.ForeignKey(
        Reclamation, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    title = models.CharField(max_length=200, verbose_name="Titre de la tâche")
    description = models.TextField(blank=True, verbose_name="Description")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reclamation_tasks'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='a_faire'
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Date limite")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['due_date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.reclamation.reference}"
