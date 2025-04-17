from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import VerificationDocumentUploadSerializer

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
