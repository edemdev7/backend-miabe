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
    phone = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=20, choices=USER_TYPES, default='particulier')
    location = models.CharField(max_length=255, blank=True, null=True)
    points = models.IntegerField(default=0)

    # Vérification du particulier
    is_phone_verified = models.BooleanField(default=False)
    cip_document = models.ImageField(upload_to='verifications/cip/', null=True, blank=True)
    residence_proof = models.ImageField(upload_to='verifications/residence/', null=True, blank=True)
    is_verified_by_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def can_submit_declaration(self):
        return self.type == 'particulier' and self.is_active and self.is_phone_verified and self.is_verified_by_admin
