# restaurant_back/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from backoffice.views import check_admin, get_csrf_token, PasswordResetRequestView, PasswordResetConfirmView
from django.http import JsonResponse

# Vue simple pour l'endpoint racine
def api_root(request):
    return JsonResponse({
        "message": "Bienvenue sur l'API du restaurant",
        "status": "OK",
        "version": "1.0",
        "documentation": "/admin/doc/",
        "login": "/backoffice/api/login/",
        "csrf_token": "/backoffice/api/get-csrf-token/"
    })

urlpatterns = [
    # Endpoint racine
    path('', api_root, name='api-root'),
    
    # Interface d'administration Django
    path('admin/', admin.site.urls),

    # Authentification JWT
    path('backoffice/api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('backoffice/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Vérification admin (protégée par IsAdminUser)
    path('backoffice/api/check-admin/', check_admin, name='check_admin'),

    # API Backoffice : schedules, réservations, etc.
    path('backoffice/api/', include('backoffice.urls')),

    # Réinitialisation du mot de passe
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/password-reset/<int:user_id>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Récupération CSRF token
    path('backoffice/api/get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]