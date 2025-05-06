from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('particulier', 'Particulier'),
        ('entreprise', 'Entreprise'),
        ('collecteur', 'Collecteur'),
        ('recycleur', 'Recycleur'),
        ('admin', 'Administrateur'),
    ]
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w\s.@+-]+$",
                message="Le nom d'utilisateur ne peut contenir que des lettres, chiffres, espaces, et @/./+/-/_"
            )
        ],
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=20, choices=USER_TYPES, default='particulier')
    location = models.CharField(max_length=255, blank=True, null=True)
    location_gps = models.CharField(max_length=100, blank=True, null=True) 
    points = models.IntegerField(default=0)

    # Vérification du particulier
    is_phone_verified = models.BooleanField(default=False)
    cip_document = models.ImageField(upload_to='verifications/cip/', null=True, blank=True)
    residence_proof = models.ImageField(upload_to='verifications/residence/', null=True, blank=True)
    rejected_reason = models.TextField(null=True, blank=True)
    is_verified_by_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def can_submit_declaration(self):
        return self.type == 'particulier' and self.is_active and self.is_phone_verified and self.is_verified_by_admin
    
    @property
    def documents_uploaded(self):
        return bool(self.cip_document and self.residence_proof)
    @property
    def verification_status(self):
        if not self.is_phone_verified:
            return "non vérifié"
        elif not self.documents_uploaded:
            return "en attente"
        elif self.is_verified_by_admin:
            return "validé"
        elif self.rejected_reason:
            return "rejeté"
        else:
            return "en attente"

class ProfessionalVerification(models.Model):
    USER_TYPES = [
        ('collecteur', 'Collecteur'),
        ('recycleur', 'Recycleur'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=USER_TYPES)

    entreprise = models.CharField(max_length=255)
    ifu = models.CharField(max_length=100)
    rccm = models.CharField(max_length=100)
    email_entreprise = models.EmailField()
    adresse_entreprise = models.CharField(max_length=255)
    type_dechets = models.CharField(max_length=255)
    nbre_equipe = models.PositiveIntegerField()
    preuve_impot = models.FileField(upload_to="verifications/impots/")

    # Spécifique aux collecteurs
    zones_intervention = models.JSONField(blank=True, null=True)

    # Admin
    is_validated = models.BooleanField(default=False)
    rejected_reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entreprise} ({self.user.username})"

class CollectorSchedule(models.Model):
    collector = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='schedules',
                                 limit_choices_to={'type': 'collecteur'})
    zone = models.CharField(max_length=255)
    day_of_week = models.IntegerField(choices=[
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ['collector', 'zone', 'day_of_week']
        ordering = ['day_of_week', 'start_time']