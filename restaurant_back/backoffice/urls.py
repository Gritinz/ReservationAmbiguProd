# backoffice/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReservationViewSet,
    ExceptionalScheduleViewSet,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

# Création du routeur pour les ViewSets DRF
router = DefaultRouter()
router.register(r'schedules', ExceptionalScheduleViewSet, basename='schedule')
router.register(r'reservations', ReservationViewSet, basename='reservation')

# Routes supplémentaires
urlpatterns = [
    # Réinitialisation du mot de passe
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<int:user_id>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Routes via router DRF (schedules, réservations)
    path('', include(router.urls)),
]