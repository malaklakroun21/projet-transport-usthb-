from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('agent', 'Agent'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='agent')

    def is_admin(self):
        return self.role == 'admin'

    def is_agent(self):
        return self.role == 'agent'
