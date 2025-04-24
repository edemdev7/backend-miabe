from rest_framework import serializers
from .models import WasteDeclaration
from users.models import CustomUser

class WasteDeclarationSerializer(serializers.ModelSerializer):
    user_username = serializers.SerializerMethodField()
    collector_username = serializers.SerializerMethodField()
    
    class Meta:
        model = WasteDeclaration
        fields = ['id', 'user', 'user_username', 'category', 'weight', 'photo', 
                  'location', 'status', 'created_at', 'collector', 'collector_username']
        read_only_fields = ['user', 'created_at']
        extra_kwargs = {
            'photo': {'required': False},
            'location': {'required': True},
            'collector': {'required': False},
        }
    
    def get_user_username(self, obj):
        return obj.user.username if obj.user else None
    
    def get_collector_username(self, obj):
        return obj.collector.username if obj.collector else None