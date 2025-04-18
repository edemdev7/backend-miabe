from django.urls import path
from .views import UploadVerificationDocumentsView,UserVerificationListView, ValidateUserView

urlpatterns = [
    path('upload-documents/', UploadVerificationDocumentsView.as_view()),
    path('admin/users/', UserVerificationListView.as_view()),
    path('admin/validate-user/<int:user_id>/', ValidateUserView.as_view()),
]
