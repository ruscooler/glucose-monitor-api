import pytest
from glucosemonitor.levels.models import Level


@pytest.mark.django_db
def test_level_creation(faker):
    level = Level.objects.create(
        user_id=faker.uuid4(),
        device_name=faker.word(),
        device_serial_number=faker.uuid4(),
        device_timestamp=faker.date_time_this_year(),
        recording_type=Level.RecordingType.HISTORY,
        glucose_history_mg_dl=faker.random_int(min=70, max=180),
        glucose_scan_mg_dl=faker.random_int(min=70, max=180),
        fast_acting_insulin=faker.word(),
        fast_acting_insulin_units=faker.random_number(digits=2),
        food_data=faker.word(),
        carbohydrates_grams=faker.random_number(digits=2),
        carbohydrates_servings=faker.random_number(digits=1),
        long_acting_insulin=faker.word(),
        long_acting_insulin_units=faker.random_number(digits=2),
        notes=faker.sentence(),
        glucose_test_strip_mg_dl=faker.random_int(min=70, max=180),
        ketone_mmol_l=faker.pyfloat(left_digits=1, right_digits=2, positive=True),
        meal_insulin_units=faker.random_number(digits=2),
        correction_insulin_units=faker.random_number(digits=2),
        user_adjusted_insulin_units=faker.random_number(digits=2)
    )
    assert level.pk is not None
    assert isinstance(level.glucose_history_mg_dl, int)
