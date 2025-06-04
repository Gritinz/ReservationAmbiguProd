# backoffice/serializers.py

from rest_framework import serializers
from .models import Reservation, ExceptionalSchedule
from datetime import date

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'name', 'date', 'time', 'party_size', 'status', 'created_at']
        read_only_fields = ['created_at']


class ExceptionalScheduleSerializer(serializers.ModelSerializer):
    mode = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = ExceptionalSchedule
        fields = ['id', 'type', 'start_date', 'end_date', 'moment', 'created_at', 'mode']
        read_only_fields = ['created_at']

    def validate(self, data):
        schedule_type = data.get('type')
        mode = data.pop('mode')

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        moment = data.get('moment')

        # --- Validation des dates et moments en fonction du mode ---
        if mode == 'single':
            if end_date:
                raise serializers.ValidationError({"end_date": "La date de fin ne doit pas être spécifiée pour une date précise."})
            if not moment:
                raise serializers.ValidationError({"moment": "Le moment (midi, soir, journée entière) est requis pour une date précise."})
            end_date_for_check = start_date  # Une seule date

        elif mode == 'range':
            if not end_date:
                raise serializers.ValidationError({"end_date": "La date de fin est requise pour une période."})
            if end_date < start_date:
                raise serializers.ValidationError({"end_date": "La date de fin ne peut pas être antérieure à la date de début."})

            # Forcer le moment à full_day pour les périodes
            if moment and moment != 'full_day':
                data['moment'] = 'full_day'

            end_date_for_check = end_date
        else:
            raise serializers.ValidationError({"mode": "Mode invalide. Doit être 'single' ou 'range'."})

        # --- Validation des jours de la semaine ---
        if start_date:
            weekday = start_date.weekday()  # Lundi=0, Dimanche=6
            if schedule_type == 'open' and weekday not in [0, 6]:
                raise serializers.ValidationError({"start_date": "Une ouverture exceptionnelle doit être un dimanche ou un lundi."})
            elif schedule_type == 'closed' and weekday in [0, 6]:
                raise serializers.ValidationError({"start_date": "Une fermeture exceptionnelle doit être un jour de semaine (mardi à samedi)."})
            elif schedule_type not in ['open', 'closed']:
                raise serializers.ValidationError({"type": "Type invalide. Doit être 'open' ou 'closed'."})

        # --- Vérification de chevauchement avec les horaires existants ---
        instance = self.instance  # Pour exclure l'instance actuelle lors de la mise à jour

        overlapping = ExceptionalSchedule.objects.filter(
            start_date__lte=end_date_for_check,
            end_date__gte=start_date
        ).exclude(pk=instance.pk if instance else None)

        if overlapping.exists():
            raise serializers.ValidationError({
                "detail": "Cette période chevauche une ouverture ou une fermeture exceptionnelle existante."
            })

        return data