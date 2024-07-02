import pytest
from django.urls import reverse
from rest_framework import status

from glucosemonitor.levels.models import Level

CSV_HEADER = "Gerät,Seriennummer,Gerätezeitstempel,Aufzeichnungstyp,Glukosewert-Verlauf mg/dL,Glukose-Scan mg/dL,Nicht numerisches schnellwirkendes Insulin,Schnellwirkendes Insulin (Einheiten),Nicht numerische Nahrungsdaten,Kohlenhydrate (Gramm),Kohlenhydrate (Portionen),Nicht numerisches Depotinsulin,Depotinsulin (Einheiten),Notizen,Glukose-Teststreifen mg/dL,Keton mmol/L,Mahlzeiteninsulin (Einheiten),Korrekturinsulin (Einheiten),Insulin-Änderung durch Anwender (Einheiten)"
CSV_DATA = "FreeStyle LibreLink,1D48A10E-DDFB-4888-8158-026F08814832,18-02-2021 11:57,0,75,,,,,,,,,,,,,,"


@pytest.mark.django_db
def test_get_levels(authorized_client, faker):
    client, user = authorized_client

    user_id = faker.uuid4()
    Level.objects.create(
        user_id=user_id,
        device_name=faker.word(),
        device_serial_number=faker.uuid4(),
        device_timestamp=faker.date_time_this_year(),
        recording_type=Level.RecordingType.HISTORY,
        glucose_history_mg_dl=faker.random_int(min=70, max=180),
        glucose_scan_mg_dl=faker.random_int(min=70, max=180)
    )

    url = reverse('level-list')
    response = client.get(url, {'user_id': user_id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1


@pytest.mark.django_db
def test_get_level_detail(authorized_client, faker):
    client, user = authorized_client

    level = Level.objects.create(
        user_id=faker.uuid4(),
        device_name=faker.word(),
        device_serial_number=faker.uuid4(),
        device_timestamp=faker.date_time_this_year(),
        recording_type=Level.RecordingType.HISTORY,
        glucose_history_mg_dl=faker.random_int(min=70, max=180),
        glucose_scan_mg_dl=faker.random_int(min=70, max=180)
    )

    url = reverse('level-detail', args=[level.pk])
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['glucose_history_mg_dl'] == level.glucose_history_mg_dl


@pytest.mark.django_db
def test_upload_csv(authorized_client, faker, tmpdir):
    client, user = authorized_client

    csv_file = tmpdir.join(f"{faker.uuid4()}.csv")
    csv_file.write(CSV_HEADER + "\n" + CSV_DATA)

    url = reverse('level-upload')
    with open(csv_file, 'rb') as f:
        response = client.post(url, {'file': f})

    assert response.status_code == status.HTTP_201_CREATED
    assert Level.objects.count() == 1


@pytest.mark.django_db
def test_aggregates_minmax_levels(authorized_client, faker):
    client, user = authorized_client

    user_id = faker.uuid4()
    date = faker.date_time_this_year()
    for _ in range(100):
        Level.objects.create(
            user_id=user_id,
            device_name=faker.word(),
            device_serial_number=faker.uuid4(),
            device_timestamp=date,
            recording_type=Level.RecordingType.HISTORY,
            glucose_history_mg_dl=faker.random_int(min=70, max=180),
            glucose_scan_mg_dl=faker.random_int(min=70, max=180)
        )
    min_max_values_q = Level.objects.get_min_max_aggregation(Level.objects.filter(user_id=user_id))
    min_max_values = min_max_values_q[0]
    url = reverse('level-maximum')
    response = client.get(url, {'user_id': user_id})

    assert response.status_code == status.HTTP_200_OK

    assert min_max_values['glucose_level_min'] == response.json()['glucose_level_min']
    assert min_max_values['glucose_level_max'] == response.json()['glucose_level_max']

