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
class MissionFilter(FilterSet):
    date_min = DateFilter(field_name="assigned_at", lookup_expr='gte')
    date_max = DateFilter(field_name="assigned_at", lookup_expr='lte')
    location = CharFilter(field_name="location", lookup_expr='icontains')
    
    class Meta:
        model = WasteDeclaration
        fields = ['status', 'location', 'date_min', 'date_max']

class WasteDeclarationViewSet(viewsets.ModelViewSet):
    queryset = WasteDeclaration.objects.all()
    serializer_class = WasteDeclarationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MissionFilter
    ordering_fields = ['assigned_at', 'status', 'location']

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
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept_mission(self, request, pk=None):
        declaration = self.get_object()
        user = request.user
        
        if user.type != 'collecteur' or declaration.collector != user:
            return Response({'error': 'Vous n\'êtes pas autorisé à accepter cette mission'}, status=403)
            
        if declaration.status != 'attribué':
            return Response({'error': 'Cette mission n\'est pas en attente d\'acceptation'}, status=400)
            
        declaration.status = 'accepté'
        declaration.accepted_at = timezone.now()
        # Si pas de date de collecte spécifiée, définir par défaut à demain
        if not declaration.collection_date:
            declaration.collection_date = timezone.now().date() + datetime.timedelta(days=1)
        declaration.save()
        
        return Response({'detail': 'Mission acceptée avec succès'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject_mission(self, request, pk=None):
        declaration = self.get_object()
        user = request.user
        
        if user.type != 'collecteur' or declaration.collector != user:
            return Response({'error': 'Vous n\'êtes pas autorisé à refuser cette mission'}, status=403)
            
        if declaration.status != 'attribué':
            return Response({'error': 'Cette mission n\'est pas en attente d\'acceptation'}, status=400)
            
        declaration.status = 'refusé'
        declaration.collector = None  # Libérer la mission pour un autre collecteur
        declaration.save()
        
        return Response({'detail': 'Mission refusée avec succès'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_collected(self, request, pk=None):
        declaration = self.get_object()
        user = request.user
        
        if user.type != 'collecteur' or declaration.collector != user:
            return Response({'error': 'Vous n\'êtes pas autorisé à marquer cette mission comme collectée'}, status=403)
            
        if declaration.status != 'accepté':
            return Response({'error': 'Cette mission doit être acceptée avant d\'être marquée comme collectée'}, status=400)
            
        declaration.status = 'collecté'
        declaration.collected_at = timezone.now()
        declaration.save()
        
        return Response({'detail': 'Mission marquée comme collectée'}) 

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def mark_all_collected(self, request):
        user = request.user
        
        if user.type != 'collecteur':
            return Response({'error': 'Action réservée aux collecteurs'}, status=403)
            
        # Optionnel: filtrer par date
        collection_date = request.data.get('collection_date', timezone.now().date().isoformat())
        
        # Marquer toutes les missions acceptées comme collectées
        declarations = WasteDeclaration.objects.filter(
            collector=user,
            status='accepté',
            collection_date=collection_date
        )
        
        count = declarations.count()
        if count == 0:
            return Response({'detail': 'Aucune mission à marquer comme collectée pour cette date'})
            
        declarations.update(
            status='collecté',
            collected_at=timezone.now()
        )
        
        return Response({'detail': f'{count} missions marquées comme collectées'})
    
    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def my_missions(self, request):
        user = request.user
        
        if user.type != 'collecteur':
            return Response({'error': 'Action réservée aux collecteurs'}, status=403)
        
        # Par défaut, on filtre sur les missions assignées ou acceptées
        status_filter = request.query_params.get('status', 'pending')
        
        if status_filter == 'pending':
            queryset = WasteDeclaration.objects.filter(
                collector=user,
                status__in=['attribué', 'accepté']
            )
        elif status_filter == 'completed':
            queryset = WasteDeclaration.objects.filter(
                collector=user,
                status='collecté'
            )
        elif status_filter == 'all':
            queryset = WasteDeclaration.objects.filter(
                collector=user
            )
        else:
            queryset = WasteDeclaration.objects.filter(
                collector=user,
                status=status_filter
            )
        
        # Appliquer les filtres standard (date, location)
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


