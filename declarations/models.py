from django.db import models
from users.models import CustomUser

class WasteDeclaration(models.Model):
    CATEGORY_CHOICES = [
        ('plastique', 'Plastique'),
        ('papier', 'Papier'),
        ('organique', 'Organique'),
        ('electronique', 'Électronique'),
        ('autre', 'Autre'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='declarations')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    weight = models.FloatField()
    photo = models.ImageField(upload_to='waste_photos/', blank=True, null=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='en attente')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.weight}kg par {self.user.username}"
