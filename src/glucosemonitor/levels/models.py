from typing import Optional

from django.db import models


class Level(models.Model):
    """
    Model to store glucose levels and related data for users.
    """

    class RecordingType(models.TextChoices):
        """
        Choices for the type of glucose recording.
        """
        HISTORY: str = "history"
        SCAN: str = "scan"

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

    def __str__(self):
        return f"{self.user_id}::{self.device_timestamp}::{self.recording_type}"
