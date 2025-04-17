from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import PhoneOTPVerifySerializer
from .models import PhoneOTP
from .serializers import PhoneOTPRequestSerializer

class PhoneOTPRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneOTPRequestSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            otp = serializer.save()
            return Response({
                "detail": "Code OTP envoyé avec succès.",
                "otp": otp
            })
        return Response(serializer.errors, status=400)

class PhoneOTPVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneOTPVerifySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Numéro vérifié avec succès "}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
