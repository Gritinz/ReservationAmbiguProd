# backoffice/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.throttling import AnonRateThrottle  # Protection anti-spam
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.db import transaction  # Pour éviter les états inconsistants

import logging

from restaurant_back.backoffice.models import ExceptionalSchedule, PasswordResetToken, Reservation
from restaurant_back.backoffice.serializers import ExceptionalScheduleSerializer, ReservationSerializer

# Initialisation du logger
logger = logging.getLogger(__name__)

# Récupération du modèle utilisateur personnalisé
User = get_user_model()

# ======================
# Réinitialisation du mot de passe
# ======================

class PasswordResetRequestView(APIView):
    """
    Vue permettant de demander une réinitialisation de mot de passe.
    Envoie un email avec un lien contenant un token unique.
    
    - Aucune authentification requise
    - Limitation du nombre de requêtes (rate limiting)
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]  # Limite à 5 tentatives/h pour anonymes

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # On retourne toujours le même message pour éviter de révéler les emails existants
            return Response({'message': 'Si cet email existe, un lien a été envoyé'}, status=status.HTTP_200_OK)

        token = get_random_string(60)

        # Lien vers ton frontend de réinitialisation
        reset_link = f"https://restaurant-front.onrender.com/reset-password/{user.id}/{token}/" 

        subject = "Réinitialisation de votre mot de passe"
        message = f"""
Bonjour {user.username},

Vous avez demandé à réinitialiser votre mot de passe. Veuillez cliquer sur le lien suivant pour continuer :
{reset_link}

Ce lien est valide pendant 1 heure.

L'équipe du restaurant
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            # Création atomique du token
            with transaction.atomic():
                PasswordResetToken.objects.create(user=user, token=token)
            logger.info(f"Email de réinitialisation envoyé à {email}")
            return Response({'message': 'Un email vous a été envoyé avec un lien de réinitialisation.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Échec de l'envoi de l'email de réinitialisation à {email} : {str(e)}", exc_info=True)
            return Response({'error': 'Une erreur est survenue lors de l\'envoi de l\'email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(APIView):
    """
    Vue permettant de confirmer la réinitialisation du mot de passe via un token valide.
    
    - Aucune authentification requise
    - Valide si le token est encore actif
    """
    permission_classes = [AllowAny]

    def post(self, request, user_id, token):
        new_password = request.data.get('new_password')

        if not new_password:
            return Response({'error': 'Mot de passe requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(token=token, user_id=user_id)
            if not reset_token.is_valid():
                return Response({'error': 'Le token a expiré ou est invalide'}, status=status.HTTP_400_BAD_REQUEST)

            user = reset_token.user
            user.set_password(new_password)
            user.save()
            reset_token.delete()  # Un token ne doit être utilisé qu'une seule fois

            logger.info(f"Mot de passe mis à jour pour l'utilisateur ID {user_id}")
            return Response({'message': 'Votre mot de passe a été mis à jour.'}, status=status.HTTP_200_OK)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Token invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation du mot de passe : {str(e)}", exc_info=True)
            return Response({'error': 'Une erreur est survenue lors de la mise à jour.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ======================
# Gestion Backoffice (réservations, horaires exceptionnels)
# ======================

class ReservationViewSet(ModelViewSet):
    """
    Vue CRUD pour les réservations.
    
    - Accès uniquement aux administrateurs
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAdminUser]


class ExceptionalScheduleViewSet(ModelViewSet):
    """
    Vue CRUD pour les horaires exceptionnels.
    
    - Accès uniquement aux administrateurs
    """
    queryset = ExceptionalSchedule.objects.all()
    serializer_class = ExceptionalScheduleSerializer
    permission_classes = [IsAdminUser]


# ======================
# Vue simple pour vérifier si l'utilisateur est admin
# ======================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def check_admin(request):
    """
    Vue utilisée pour vérifier si l'utilisateur connecté est admin.
    
    - Nécessite d'être authentifié et admin
    """
    return Response({'is_admin': True})


# ======================
# Vue pour récupérer le CSRF Token
# ======================

def get_csrf_token(request):
    """
    Retourne le CSRF token au frontend sous forme de JSON.
    
    - Utile pour les requêtes POST sans connexion Django
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})