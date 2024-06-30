import pytest
from rest_framework.test import APIClient
from faker import Faker


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def authorized_client(django_user_model):
    client = APIClient()
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')
    return client, user
