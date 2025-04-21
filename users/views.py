from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, status
from .serializers import ProfessionalVerificationSerializer, VerificationDocumentUploadSerializer
from .models import CustomUser
from .serializers import UserVerificationAdminSerializer

class UploadVerificationDocumentsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.type != 'particulier':
            return Response({"error": "Cette opération est réservée aux particuliers."}, status=403)

        serializer = VerificationDocumentUploadSerializer(
            instance=request.user,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Documents envoyés. En attente de validation par l'administration."})
        return Response(serializer.errors, status=400)


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == 'admin'

# Lister tous les utilisateurs particuliers
class UserVerificationListView(generics.ListAPIView):
    serializer_class = UserVerificationAdminSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return CustomUser.objects.filter(type='particulier')

# Valider ou refuser un utilisateur
class ValidateUserView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id, type='particulier')
        except CustomUser.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=404)

        action = request.data.get("action")
        message = request.data.get("message", "")

        if action == "approve":
            user.is_active = True
            user.is_verified_by_admin = True
            user.rejected_reason = None
        elif action == "reject":
            user.is_active = False
            user.is_verified_by_admin = False
            user.rejected_reason = message or "Document non valide."
        else:
            return Response({"error": "Action invalide."}, status=400)

        user.save()
        return Response({"detail": "Compte mis à jour avec succès."})
    
class SubmitProfessionalVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if hasattr(user, 'professionalverification'):
            return Response({"detail": "Demande déjà soumise."}, status=400)

        serializer = ProfessionalVerificationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Demande soumise avec succès. En attente de validation."})
        return Response(serializer.errors, status=400)
