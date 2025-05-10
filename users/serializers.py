from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import CollectorSchedule, CustomUser, ProfessionalVerification
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
        # Supprimer le type des données validées s'il existe déjà
        if 'type' in validated_data:
            validated_data.pop('type')
        # Création avec le type de l'utilisateur
        return ProfessionalVerification.objects.create(user=user, type=user.type, **validated_data)

class UserSerializer(BaseUserSerializer):
    phone_verified = serializers.SerializerMethodField()
    documents_uploaded = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()
    pro_verification_submitted = serializers.SerializerMethodField()
    pro_verification_status = serializers.SerializerMethodField()
    professional_verification = ProfessionalVerificationSerializer(read_only=True,source='professionalverification')


    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'type', 'location', 'points',
                  'is_active', 'phone_verified', 'documents_uploaded',
                  'verification_status', 'rejected_reason',
                  'pro_verification_submitted', 'pro_verification_status',
                  'professional_verification', 'is_available','phone','location_gps') # Added professional_verification here
        read_only_fields = BaseUserSerializer.Meta.read_only_fields + ('professional_verification',)


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
            # Utilise hasattr pour une vérification plus sûre sans exception directe
            return hasattr(obj, 'professionalverification') and obj.professionalverification is not None
        except ProfessionalVerification.DoesNotExist: # Garde pour robustesse
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
    # Ajoute le serializer imbriqué pour les données professionnelles
    professional_verification = ProfessionalVerificationSerializer(read_only=True, source='professionalverification')
    # Ajoute un champ pour le statut de la vérification pro
    pro_verification_status = serializers.SerializerMethodField()
    pro_verification_submitted = serializers.SerializerMethodField() 


    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'type', 'is_active',
                  'is_phone_verified', 'is_verified_by_admin', # Pour les particuliers
                  'cip_document', 'residence_proof', 'rejected_reason', # Pour les particuliers
                  'professional_verification', # Pour collecteurs/recycleurs
                  'pro_verification_status','pro_verification_submitted'] # Pour collecteurs/recycleurs
        read_only_fields = ['id', 'username', 'email', 'phone', 'type',
                            'is_phone_verified', 'cip_document', 'residence_proof',
                            'professional_verification'] # Marque les champs imbriqués comme read_only
    def get_pro_verification_submitted(self, obj):
        if obj.type not in ['collecteur', 'recycleur']:
            return None
        try:
            # Utilise hasattr pour une vérification plus sûre sans exception directe
            return hasattr(obj, 'professionalverification') and obj.professionalverification is not None
        except ProfessionalVerification.DoesNotExist: # Garde pour robustesse
            return False

    def get_pro_verification_status(self, obj):
        # Réutilise la logique de UserSerializer si possible, ou la réimplémente ici
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


class CollectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'location', 'is_active']
        read_only_fields = fields

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'location', 'location_gps']
        extra_kwargs = {
            'username': {'required': False},
            'phone': {'required': False},
            'location': {'required': False},
            'location_gps': {'required': False}
        }
    
    def update(self, instance, validated_data):
        # Vérifie si le numéro de téléphone a changé
        old_phone = instance.phone
        new_phone = validated_data.get('phone')
        
        user = super().update(instance, validated_data)
        
        # Si le numéro de téléphone a changé, réinitialiser la vérification
        if new_phone and new_phone != old_phone:
            user.is_phone_verified = False
            user.save()
            
        return user
    
class CollectorScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CollectorSchedule
        fields = ['id', 'zone', 'day_of_week', 'day_name', 'start_time', 'end_time']
        read_only_fields = ['id']
    
    def get_day_name(self, obj):
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        return days[obj.day_of_week]