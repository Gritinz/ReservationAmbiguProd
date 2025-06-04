from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_in = models.IntegerField(default=3600)  # 1h en secondes

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < self.expires_in

    def __str__(self):
        return f"Token pour {self.user.email}"


# ========== Modèle : Horaires exceptionnels ==========
class ExceptionalSchedule(models.Model):
    TYPE_CHOICES = (
        ('open', 'Ouverture exceptionnelle'),
        ('closed', 'Fermeture exceptionnelle'),
    )
    MOMENT_CHOICES = (
        ('full_day', 'Toute la journée'),
        ('lunch', 'Midi'),
        ('dinner', 'Soir'),
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Null pour une seule date
    moment = models.CharField(max_length=10, choices=MOMENT_CHOICES, default='full_day')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Horaire exceptionnel"
        verbose_name_plural = "Horaires exceptionnels"
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['type']),
        ]

    def clean(self):
        """Validation simple lors de l'enregistrement"""
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")

    def __str__(self):
        return f"{self.get_type_display()} - {self.start_date}"


# ========== Modèle : Réservations ==========
class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()  # Optionnel mais utile pour les mails
    phone = models.CharField(max_length=20, blank=True, null=True)  # Pour le contact
    date = models.DateField()
    time = models.TimeField()
    party_size = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['date', 'time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} - {self.date} à {self.time}"