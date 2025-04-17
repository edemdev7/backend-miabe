from django.urls import path
from .views import UploadVerificationDocumentsView

urlpatterns = [
    path('upload-documents/', UploadVerificationDocumentsView.as_view()),
]
