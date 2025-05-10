from rest_framework import serializers
from .models import WasteDeclaration
from users.models import CustomUser
from django.utils import timezone
from django.core.exceptions import ValidationError

class WasteDeclarationSerializer(serializers.ModelSerializer):
    user_username = serializers.SerializerMethodField()
    user_phone = serializers.SerializerMethodField()  # Nouveau champ
    user_location_gps = serializers.SerializerMethodField()  # Nouveau champ
    collector_username = serializers.SerializerMethodField()
    # collector_phone = serializers.SerializerMethodField()  # Nouveau champ
    # collector_location_gps = serializers.SerializerMethodField()  # Nouveau champ
    days_since_assignment = serializers.SerializerMethodField()
    
    class Meta:
        model = WasteDeclaration
        fields = ['id', 'user', 'user_username', 'user_phone', 'user_location_gps',
                  'category', 'weight', 'photo', 'location', 'status', 
                  'created_at', 'collector', 'collector_username',  'assigned_at', 'accepted_at', 
                  'collected_at', 'collection_date', 'days_since_assignment']
        read_only_fields = ['user', 'created_at', 'assigned_at', 'accepted_at', 'collected_at']
        extra_kwargs = {
            'photo': {'required': False},
            'location': {'required': True},
            'collector': {'required': False},
            'collection_date': {'required': False},
        }
    
    def get_user_username(self, obj):
        return obj.user.username if obj.user else None
    
    def get_user_phone(self, obj):
        return obj.user.phone if obj.user else None
    
    def get_user_location_gps(self, obj):
        return obj.user.location_gps if obj.user else None
    
    def get_collector_username(self, obj):
        return obj.collector.username if obj.collector else None
    
    # def get_collector_phone(self, obj):
    #     return obj.collector.phone if obj.collector else None
    
    # def get_collector_location_gps(self, obj):
    #     return obj.collector.location_gps if obj.collector else None
    
    def get_days_since_assignment(self, obj):
        if obj.assigned_at:
            delta = timezone.now() - obj.assigned_at
            return delta.days
        return None