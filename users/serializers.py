from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import CustomUser, ProfessionalVerification
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'type', 'location', 'points', 'is_phone_verified', 'is_verified_by_admin', 'rejected_reason')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        if user.type == 'particulier':
            user.is_active = True
            user.save()
        return user

class UserSerializer(BaseUserSerializer):
    phone_verified = serializers.SerializerMethodField()
    documents_uploaded = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()
    pro_verification_submitted = serializers.SerializerMethodField()
    pro_verification_status = serializers.SerializerMethodField()


    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'type', 'location', 'points',
                  'is_active', 'phone_verified', 'documents_uploaded',
                  'verification_status', 'rejected_reason',
                  'pro_verification_submitted', 'pro_verification_status')


    def get_phone_verified(self, obj):
        return obj.is_phone_verified

    def get_documents_uploaded(self, obj):
        return bool(obj.cip_document and obj.residence_proof)

    def get_verification_status(self, obj):
        if not obj.is_phone_verified:
            return "non vérifié"
        elif not (obj.cip_document and obj.residence_proof):
            return "en attente"
        elif obj.is_verified_by_admin:
            return "validé"
        elif obj.rejected_reason:
            return "rejeté"
        return "en attente"
    def get_pro_verification_submitted(self, obj):
        if obj.type not in ['collecteur', 'recycleur']:
            return None
        try:
            return bool(obj.professionalverification)
        except ProfessionalVerification.DoesNotExist:
            return False
    
    def get_pro_verification_status(self, obj):
        if obj.type not in ['collecteur', 'recycleur']:
            return None
        
        try:
            pro_verif = obj.professionalverification
        except ProfessionalVerification.DoesNotExist:
            return "non soumis"
            
        if pro_verif.is_validated:
            return "validé"
        elif pro_verif.rejected_reason:
            return "rejeté"
        else:
            return "en attente"


class VerificationDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['cip_document', 'residence_proof']

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_phone_verified:
            raise serializers.ValidationError("Votre téléphone n'est pas encore vérifié.")
        return data
    
class UserVerificationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'type', 'is_active',
                  'is_phone_verified', 'is_verified_by_admin',
                  'cip_document', 'residence_proof', 'rejected_reason']

class ProfessionalVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalVerification
        exclude = ['is_validated', 'rejected_reason', 'submitted_at', 'user']

    def validate(self, data):
        user = self.context['request'].user
        if user.type not in ['collecteur', 'recycleur']:
            raise serializers.ValidationError("Ce formulaire est réservé aux collecteurs et recycleurs.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return ProfessionalVerification.objects.create(user=user, type=user.type, **validated_data)

class CollectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'location', 'is_active']
        read_only_fields = fields