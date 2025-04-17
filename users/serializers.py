from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import CustomUser
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'type', 'location')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        if user.type == 'particulier':
            user.is_active = False
            user.save()
        return user

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'type', 'location', 'points')

class VerificationDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['cip_document', 'residence_proof']

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_phone_verified:
            raise serializers.ValidationError("Votre téléphone n'est pas encore vérifié.")
        return data