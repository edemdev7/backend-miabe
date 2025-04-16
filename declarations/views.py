from rest_framework import viewsets, permissions
from .models import WasteDeclaration
from .serializers import WasteDeclarationSerializer

class WasteDeclarationViewSet(viewsets.ModelViewSet):
    queryset = WasteDeclaration.objects.all()
    serializer_class = WasteDeclarationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Retourne uniquement les déclarations de l'utilisateur connecté
        return WasteDeclaration.objects.filter(user=self.request.user)
