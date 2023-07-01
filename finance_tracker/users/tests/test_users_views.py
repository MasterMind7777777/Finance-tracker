import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='12345')

def test_signup_view(client):
    response = client.get(reverse('users:signup'))
    assert response.status_code == 200

def test_user_login_view(client, user):
    response = client.post(reverse('users:login'), {'username': 'testuser', 'password': '12345'})
    assert response.status_code == 302

def test_user_logout_view(client, user):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('users:logout'))
    assert response.status_code == 302

def test_dashboard_view(client, user):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('users:dashboard'))
    assert response.status_code == 200

# Continue with other views...
