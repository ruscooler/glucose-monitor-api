from typing import Optional

from django.db import models
from django.db.models import Manager, Case, When, Value, Min, Max


class LevelManager(Manager):
    """
    Custom manager for the Level model
    """

    def get_min_max_aggregation(self, qs):
        """
        Aggregate minimum and maximum glucose levels for the given queryset.
        """
        glucose_value_q = Case(
            When(recording_type=Level.RecordingType.HISTORY, then='glucose_history_mg_dl'),
            When(recording_type=Level.RecordingType.SCAN, then='glucose_scan_mg_dl'),
            default=Value(0),
        )
        return qs.filter(
            recording_type__in=[Level.RecordingType.HISTORY, Level.RecordingType.SCAN]
        ).values('user_id').annotate(
            glucose_level_min=Min(glucose_value_q),
            glucose_level_max=Max(glucose_value_q),
        )


class Level(models.Model):
    """
    Model to store glucose levels and related data for users.
    """

    class RecordingType(models.TextChoices):
        """
        Choices for the type of glucose recording.
        """
        HISTORY: str = "0"
        SCAN: str = "1"

        @classmethod
        def get_type_by_int_value(cls, value: int) -> Optional[str]:
            return {
                0: cls.HISTORY,
                1: cls.SCAN,
            }.get(value)

    user_id = models.UUIDField(db_index=True)
    device_name = models.CharField(max_length=100)
    device_serial_number = models.UUIDField(db_index=True)
    device_timestamp = models.DateTimeField(db_index=True)

    recording_type = models.CharField(choices=RecordingType.choices, db_index=True, max_length=15)
    glucose_history_mg_dl = models.IntegerField(null=True, blank=True)
    glucose_scan_mg_dl = models.IntegerField(null=True, blank=True)

    fast_acting_insulin = models.CharField(max_length=100, null=True, blank=True)
    fast_acting_insulin_units = models.FloatField(null=True, blank=True)

    food_data = models.CharField(max_length=100, null=True, blank=True)

    carbohydrates_grams = models.FloatField(null=True, blank=True)
    carbohydrates_servings = models.FloatField(null=True, blank=True)

    long_acting_insulin = models.CharField(max_length=100, null=True, blank=True)
    long_acting_insulin_units = models.FloatField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    glucose_test_strip_mg_dl = models.IntegerField(null=True, blank=True)
    ketone_mmol_l = models.FloatField(null=True, blank=True)

    meal_insulin_units = models.FloatField(null=True, blank=True)
    correction_insulin_units = models.FloatField(null=True, blank=True)
    user_adjusted_insulin_units = models.FloatField(null=True, blank=True)

    objects = LevelManager()

    def __str__(self):
        return f"{self.user_id}::{self.device_timestamp}::{self.recording_type}"
