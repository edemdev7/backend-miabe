from django.urls import path
from .views import AdminProfessionalVerificationListView, AdminValidateProfessionalView, SubmitProfessionalVerificationView, UploadVerificationDocumentsView,UserVerificationListView, ValidateUserView

urlpatterns = [
    path('upload-documents/', UploadVerificationDocumentsView.as_view()),
    path('admin/users/', UserVerificationListView.as_view()),
    path('admin/validate-user/<int:user_id>/', ValidateUserView.as_view()),
    path('professional-verification/', SubmitProfessionalVerificationView.as_view()),
    path('admin/verifications/', AdminProfessionalVerificationListView.as_view()),
    path('admin/verifications/<int:verification_id>/', AdminValidateProfessionalView.as_view()),
]
