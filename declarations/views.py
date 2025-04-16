from rest_framework import viewsets, permissions
from .models import WasteDeclaration
from .serializers import WasteDeclarationSerializer
from users.models import CustomUser

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
        declaration = serializer.save(user=self.request.user)
        # Calcul des points
        points = int(declaration.weight * POINTS_PER_KG.get(declaration.category, 1))
        # Mise à jour des points utilisateur
        user = self.request.user
        user.points += points
        user.save()

    def get_queryset(self):
        # Retourne uniquement les déclarations de l'utilisateur connecté
        return WasteDeclaration.objects.filter(user=self.request.user)
