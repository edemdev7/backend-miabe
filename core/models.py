from django.db import models
from users.models import CustomUser
import random

class PhoneOTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.save()
        return self.otp_code
