from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CollectorAvailabilityView, AdminProfessionalVerificationListView, AdminValidateProfessionalView, SubmitProfessionalVerificationView, UploadVerificationDocumentsView,UserVerificationListView, ValidateUserView,CollectorListView, CollectorScheduleViewSet, UserProfileUpdateView


router = DefaultRouter()
router.register(r'collector-schedules', CollectorScheduleViewSet, basename='collector-schedules')

urlpatterns = [
    path('upload-documents/', UploadVerificationDocumentsView.as_view()),
    path('admin/users/', UserVerificationListView.as_view()),
    path('admin/validate-user/<int:user_id>/', ValidateUserView.as_view()),
    path('professional-verification/', SubmitProfessionalVerificationView.as_view()),
    path('admin/verifications/', AdminProfessionalVerificationListView.as_view()),
    path('admin/validate-professional/<int:verification_id>/', AdminValidateProfessionalView.as_view()),
    path('collectors/', CollectorListView.as_view(), name='collector-list'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('collector/availability/', CollectorAvailabilityView.as_view(), name='collector-availability'),
    path('', include(router.urls)),
]
# This file defines the URL routing for the users app in a Django project.