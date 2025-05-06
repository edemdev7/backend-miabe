from django.db import models
from users.models import CustomUser
from django.utils import timezone

class WasteDeclaration(models.Model):
    CATEGORY_CHOICES = [
        ('plastique', 'Plastique'),
        ('papier', 'Papier'),
        ('organique', 'Organique'),
        ('electronique', 'Électronique'),
        ('autre', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('en attente', 'En attente'),
        ('attribué', 'Attribué'),
        ('accepté', 'Accepté'),
        ('refusé', 'Refusé'),
        ('collecté', 'Collecté'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='declarations')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    weight = models.FloatField()
    photo = models.ImageField(upload_to='waste_photos/', blank=True, null=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en attente')
    created_at = models.DateTimeField(auto_now_add=True)
    collector = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collected_declarations',
        limit_choices_to={'type': 'collecteur'}
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    collection_date = models.DateField(null=True, blank=True, help_text="Date prévue pour la collecte")
    
    def __str__(self):
        return f"{self.category} - {self.weight}kg par {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Si le statut passe à "attribué", enregistrer la date d'attribution
        if self.status == 'attribué' and not self.assigned_at:
            self.assigned_at = timezone.now()
        # Si le statut passe à "accepté", enregistrer la date d'acceptation
        elif self.status == 'accepté' and not self.accepted_at:
            self.accepted_at = timezone.now()
        # Si le statut passe à "collecté", enregistrer la date de collecte
        elif self.status == 'collecté' and not self.collected_at:
            self.collected_at = timezone.now()
        super().save(*args, **kwargs)