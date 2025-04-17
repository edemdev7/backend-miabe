from django.urls import path
from .views import PhoneOTPRequestView, PhoneOTPVerifyView

urlpatterns = [
    path('request-otp/', PhoneOTPRequestView.as_view()),
    path('verify-phone/', PhoneOTPVerifyView.as_view()),
]
