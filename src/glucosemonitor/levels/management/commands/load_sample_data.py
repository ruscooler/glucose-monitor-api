import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz
from django.core.management.base import BaseCommand
from django.conf import settings

from glucosemonitor.levels.models import Level

logger = logging.getLogger(__name__)
default_timezone = pytz.timezone(settings.TIME_ZONE)

COLUMNS = {
    'DEVICE_NAME': 'Gerät',
    'DEVICE_SERIAL_NUMBER': 'Seriennummer',
    'DEVICE_TIMESTAMP': 'Gerätezeitstempel',
    'RECORDING_TYPE': 'Aufzeichnungstyp',
    'GLUCOSE_HISTORY_MG_DL': 'Glukosewert-Verlauf mg/dL',
    'GLUCOSE_SCAN_MG_DL': 'Glukose-Scan mg/dL',
    'FAST_ACTING_INSULIN': 'Nicht numerisches schnellwirkendes Insulin',
    'FAST_ACTING_INSULIN_UNITS': 'Schnellwirkendes Insulin (Einheiten)',
    'FOOD_DATA': 'Nicht numerische Nahrungsdaten',
    'CARBS_GRAMS': 'Kohlenhydrate (Gramm)',
    'CARBS_SERVINGS': 'Kohlenhydrate (Portionen)',
    'LONG_ACTING_INSULIN': 'Nicht numerisches Depotinsulin',
    'LONG_ACTING_INSULIN_UNITS': 'Depotinsulin (Einheiten)',
    'NOTES': 'Notizen',
    'GLUCOSE_TEST_STRIP_MG_DL': 'Glukose-Teststreifen mg/dL',
    'KETONE_MMOL_L': 'Keton mmol/L',
    'MEAL_INSULIN_UNITS': 'Mahlzeiteninsulin (Einheiten)',
    'CORRECTION_INSULIN_UNITS': 'Korrekturinsulin (Einheiten)',
    'USER_ADJUSTED_INSULIN_UNITS': 'Insulin-Änderung durch Anwender (Einheiten)'
}


class Command(BaseCommand):
    help = "Load sample data from CSV file intro the Level mode"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file_path",
            type=Path,
            help="The path to the CSV file to be loaded",
        )
        parser.add_argument(
            "--chunk_size",
            type=int,
            default=1000,
            help="Number of rows to process in each chunk",
        )

    def handle(self, *args, **options):
        csv_file_path: Path = options['csv_file_path']
        chunk_size: int = options['chunk_size']
        objects = []

        user_id = csv_file_path.stem

        pd_chunk_dataframe = pd.read_csv(
            csv_file_path,
            chunksize=chunk_size,
            skiprows=2,
            dtype={
                COLUMNS['DEVICE_NAME']: str,
                COLUMNS['DEVICE_SERIAL_NUMBER']: str,
                COLUMNS['DEVICE_TIMESTAMP']: str,
                COLUMNS['RECORDING_TYPE']: str,
                COLUMNS['GLUCOSE_HISTORY_MG_DL']: float,
                COLUMNS['GLUCOSE_SCAN_MG_DL']: float,
                COLUMNS['FAST_ACTING_INSULIN']: str,
                COLUMNS['FAST_ACTING_INSULIN_UNITS']: float,
                COLUMNS['FOOD_DATA']: str,
                COLUMNS['CARBS_GRAMS']: float,
                COLUMNS['CARBS_SERVINGS']: float,
                COLUMNS['LONG_ACTING_INSULIN']: str,
                COLUMNS['LONG_ACTING_INSULIN_UNITS']: float,
                COLUMNS['NOTES']: str,
                COLUMNS['GLUCOSE_TEST_STRIP_MG_DL']: float,
                COLUMNS['KETONE_MMOL_L']: float,
                COLUMNS['MEAL_INSULIN_UNITS']: float,
                COLUMNS['CORRECTION_INSULIN_UNITS']: float,
                COLUMNS['USER_ADJUSTED_INSULIN_UNITS']: float
            },
        )
        for chunk in pd_chunk_dataframe:
            chunk = chunk.replace({float('nan'): None})

            for i, row in chunk.iterrows():

                objects.append(
                    Level(
                        user_id=user_id,
                        device_name=row[COLUMNS['DEVICE_NAME']],
                        device_serial_number=row[COLUMNS['DEVICE_SERIAL_NUMBER']],
                        device_timestamp=default_timezone.localize(
                            datetime.strptime(row[COLUMNS['DEVICE_TIMESTAMP']], "%d-%m-%Y %H:%M")
                        ),
                        recording_type=row[COLUMNS['RECORDING_TYPE']],
                        glucose_history_mg_dl=row.get(COLUMNS['GLUCOSE_HISTORY_MG_DL']),
                        glucose_scan_mg_dl=row.get(COLUMNS['GLUCOSE_SCAN_MG_DL']),
                        fast_acting_insulin=row.get(COLUMNS['FAST_ACTING_INSULIN']),
                        fast_acting_insulin_units=row.get(COLUMNS['FAST_ACTING_INSULIN_UNITS']),
                        food_data=row.get(COLUMNS['FOOD_DATA']),
                        carbohydrates_grams=row.get(COLUMNS['CARBS_GRAMS']),
                        carbohydrates_servings=row.get(COLUMNS['CARBS_SERVINGS']),
                        long_acting_insulin=row.get(COLUMNS['LONG_ACTING_INSULIN']),
                        long_acting_insulin_units=row.get(COLUMNS['LONG_ACTING_INSULIN_UNITS']),
                        notes=row.get(COLUMNS['NOTES']),
                        glucose_test_strip_mg_dl=row.get(COLUMNS['GLUCOSE_TEST_STRIP_MG_DL']),
                        ketone_mmol_l=row.get(COLUMNS['KETONE_MMOL_L']),
                        meal_insulin_units=row.get(COLUMNS['MEAL_INSULIN_UNITS']),
                        correction_insulin_units=row.get(COLUMNS['CORRECTION_INSULIN_UNITS']),
                        user_adjusted_insulin_units=row.get(COLUMNS['USER_ADJUSTED_INSULIN_UNITS'])
                    )
                )

            if len(objects) >= chunk_size:
                Level.objects.bulk_create(objects)
                objects.clear()
        if objects:
            Level.objects.bulk_create(objects)

        print('Successfully imported data from {}'.format(csv_file_path))
