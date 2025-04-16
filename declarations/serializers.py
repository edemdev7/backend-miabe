from rest_framework import serializers
from .models import WasteDeclaration

class WasteDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteDeclaration
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
        extra_kwargs = {
            'photo': {'required': False},
            'location': {'required': True},
        }