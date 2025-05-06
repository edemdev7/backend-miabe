from rest_framework import viewsets, permissions, serializers
from rest_framework.decorators import action
from .models import WasteDeclaration
from .serializers import WasteDeclarationSerializer
from users.models import CustomUser
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
import datetime
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter, CharFilter


POINTS_PER_KG = {
    'plastique': 5,
    'papier': 3,
    'organique': 2,
    'electronique': 10,
    'autre': 1,
}

class WasteDeclarationViewSet(viewsets.ModelViewSet):
    queryset = WasteDeclaration.objects.all()
    serializer_class = WasteDeclarationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user= self.request.user
        if user.type != 'particulier':
            raise serializers.ValidationError("Cette opération est réservée aux particuliers.")
        if not user.is_verified_by_admin:
            raise serializers.ValidationError("Votre compte n'est pas encore vérifié par l'administration.")
        
        declaration = serializer.save(user=self.request.user)
        # Calcul des points
        points = int(declaration.weight * POINTS_PER_KG.get(declaration.category, 1))
        # Mise à jour des points utilisateur
        user = self.request.user
        user.points += points
        user.save()

    def get_queryset(self):
        # Retourne uniquement les déclarations de l'utilisateur connecté
        user = self.request.user
        if user.type == 'admin':
            return WasteDeclaration.objects.all()
        
        return WasteDeclaration.objects.filter(user=user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def assign_collector(self, request, pk=None):
        declaration = self.get_object()
        collector_id = request.data.get('collector_id')
        try:
            collector = CustomUser.objects.get(id=collector_id, type='collecteur', location=declaration.location)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Aucun collecteur trouvé dans cette zone.'}, status=400)
        declaration.collector = collector
        declaration.status = 'attribué'
        declaration.save()
        return Response({'detail': 'Collecteur attribué avec succès.'})

class MissionFilter(FilterSet):
    date_min = DateFilter(field_name="assigned_at", lookup_expr='gte')
    date_max = DateFilter(field_name="assigned_at", lookup_expr='lte')
    location = CharFilter(field_name="location", lookup_expr='icontains')
    
    class Meta:
        model = WasteDeclaration
        fields = ['status', 'location', 'date_min', 'date_max']
