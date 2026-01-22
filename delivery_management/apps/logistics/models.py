from django import forms
from django.db import models
<<<<<<< HEAD
from django.utils import timezone
=======
from clients.models import Client
from delivery_management.delivery_management import settings

class Driver(models.Model):
    id_driver = models.DecimalField(max_digits=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    available = models.BooleanField(default=True)
>>>>>>> Django-models


class Chauffeur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nom


class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.immatriculation


class Tournee(models.Model):
    date = models.DateField(default=timezone.now)
    chauffeur = models.ForeignKey('logistics.Chauffeur', on_delete=models.PROTECT)
    vehicule = models.ForeignKey('logistics.Vehicule', on_delete=models.PROTECT)

    def __str__(self):
        return f"Tournée {self.date}"


class TypeService(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Destination(models.Model):
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=20)
    pays = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.ville} ({self.pays})"

<<<<<<< HEAD


class Expedition(models.Model):

    poids = models.FloatField()
    volume = models.FloatField()
    description = models.TextField()
    montant_total = models.FloatField()
    numero_suivi = models.CharField(max_length=30, unique=True)
    
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

    date_creation = models.DateTimeField(auto_now_add=True)
    date_livraison_estimee = models.DateField()
    date_livraison_reelle = models.DateField(
        null=True,
        blank=True
    )

    # foreign keys 
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='expeditions'
    )

    destination = models.ForeignKey(
        'logistics.Destination',
        on_delete=models.PROTECT
    )

    type_service = models.ForeignKey(
        'logistics.TypeService',
        on_delete=models.PROTECT
    )

    tournee = models.ForeignKey(
        'logistics.Tournee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

=======
>>>>>>> Django-models
