from django.db import models

class Clients(models.Model):

    CLIENT_TYPE_CHOICES = [
        ('Actif', 'Actif'),
        ('Inactif', 'Inactif'),
    ]

    code_client = models.CharField(max_length=20, unique=True)
class Client(models.Model):
    code_client = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField()

    client_type = models.CharField(
        max_length=50,
        choices=CLIENT_TYPE_CHOICES
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    client_type = models.CharField(max_length=50)

    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
