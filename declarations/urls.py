from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WasteDeclarationViewSet

router = DefaultRouter()
router.register(r'waste', WasteDeclarationViewSet, basename='waste')

urlpatterns = [
    path('', include(router.urls)),
]
# This file defines the URL routing for the Waste Declaration API.
# It uses Django's URL dispatcher to map URLs to views.
# The `DefaultRouter` automatically generates the necessary URL patterns for the
# `WasteDeclarationViewSet`, which handles the CRUD operations for waste declarations.
# The `urlpatterns` list includes the base URL for the API, which is prefixed with 'api/'.