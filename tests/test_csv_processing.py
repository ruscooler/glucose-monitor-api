import pytest
from pathlib import Path
from glucosemonitor.levels.utils.csv_processing import process_csv_file
from glucosemonitor.levels.models import Level


@pytest.mark.django_db
def test_process_csv_file(faker, tmpdir):
    csv_file = tmpdir.join("sample.csv")
    csv_file.write(f"""Gerät,Seriennummer,Gerätezeitstempel,Aufzeichnungstyp,Glukosewert-Verlauf mg/dL,Glukose-Scan mg/dL
{faker.word()},{faker.uuid4()},{faker.date_time_this_year().strftime('%d-%m-%Y %H:%M')},history,{faker.random_int(min=70, max=180)},{faker.random_int(min=70, max=180)}
""")

    process_csv_file(Path(csv_file), faker.uuid4())

    assert Level.objects.count() == 1