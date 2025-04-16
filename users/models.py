from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('particulier', 'Particulier'),
        ('entreprise', 'Entreprise'),
        ('collecteur', 'Collecteur'),
        ('recycleur', 'Recycleur'),
        ('admin', 'Administrateur'),
    ]
    
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=USER_TYPES, default='particulier')
    location = models.CharField(max_length=255, blank=True, null=True)
    points = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.type})"
