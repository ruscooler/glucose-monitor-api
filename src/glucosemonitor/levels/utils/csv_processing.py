from datetime import datetime, tzinfo
from io import StringIO
from logging import Logger, getLogger
from pathlib import Path

import pandas as pd
import pytz
from pandas import DataFrame
from pandas.io.parsers import TextFileReader

from glucosemonitor import settings
from glucosemonitor.levels.models import Level

logger: Logger = getLogger(__name__)


default_timezone: tzinfo = pytz.timezone(settings.TIME_ZONE)

COLUMNS: dict = {
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


def read_csv_content_and_find_header(csv_file: Path, max_lines: int = 20) -> tuple[StringIO, int]:
    buffer = []
    header_row = None

    try:
        with open(csv_file, 'r') as file:
            lines: str = file.readlines()
            for i, line in enumerate(lines):
                buffer.append(line)
                if COLUMNS['DEVICE_NAME'] in line and COLUMNS['DEVICE_SERIAL_NUMBER'] in line:
                    header_row = i
                if i >= max_lines and header_row is None:
                    break
        if header_row is None:
            raise ValueError("Unable to find header row in the CSV file.")
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise

    stream = StringIO(''.join(buffer))
    return stream, header_row


def process_csv_file(csv_file_path: Path, user_id: str, chunk_size: int = 10000):
    try:
        stream, header_line = read_csv_content_and_find_header(csv_file_path)
        pd_chunk_dataframe: TextFileReader = pd.read_csv(
            stream,
            chunksize=chunk_size,
            skiprows=header_line,
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

        objects = []
        chunk_df: DataFrame
        for chunk_df in pd_chunk_dataframe:
            chunk_df = chunk_df.replace({float('nan'): None})
            for i, row in chunk_df.iterrows():
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
    except Exception as e:
        logger.exception(f"Failed to import data from {csv_file_path}: {e}")
        raise
