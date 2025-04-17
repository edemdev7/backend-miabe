from rest_framework import serializers
from users.models import CustomUser
from .models import PhoneOTP

class PhoneOTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Le numéro doit contenir uniquement des chiffres.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.phone = self.validated_data['phone']
        user.save()
        otp_obj, _ = PhoneOTP.objects.get_or_create(user=user)
        otp = otp_obj.generate_code()
        print(f"[DEBUG] OTP envoyé au {user.phone} : {otp}")  # À remplacer par un vrai SMS plus tard
        return otp

class PhoneOTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        user = self.context['request'].user
        try:
            otp_obj = PhoneOTP.objects.get(user=user)
        except PhoneOTP.DoesNotExist:
            raise serializers.ValidationError("Aucun code OTP trouvé pour cet utilisateur.")

        if data['otp'] != otp_obj.otp_code:
            raise serializers.ValidationError("Code OTP incorrect.")
        
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.is_phone_verified = True
        user.save()
        PhoneOTP.objects.filter(user=user).delete()
        return user
