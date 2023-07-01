import datetime
import pytest
import json
from django.utils.timezone import make_aware
from django.core import serializers
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Category

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', password='12345')
    category = Category.objects.create(name='Test Category', user=user)
    return user

def test_add_transaction_view(client, user):
    client.login(username='testuser', password='12345')
    category = Category.objects.first()
    transaction_date = make_aware(datetime.datetime(2023, 7, 1))  # Add the appropriate timezone information
    response = client.post(reverse('transactions:add_transaction'), {
        'title': 'Test Transaction',
        'description': 'This is a test transaction.',
        'amount': 100.0,
        'category': category.id,
        'date': transaction_date,
    })
    assert response.status_code == 302
    assert response.url == reverse('users:dashboard')
    assert Transaction.objects.filter(title='Test Transaction').exists()

def test_delete_transaction_view(client, user):
    client.login(username='testuser', password='12345')
    transaction_date = make_aware(datetime.datetime(2023, 7, 1))  # Add the appropriate timezone information
    transaction = Transaction.objects.create(
        title='Test Transaction',
        description='This is a test transaction.',
        amount=100.0,
        category=Category.objects.first(),
        date=transaction_date,
        user=user
    )
    response = client.post(reverse('transactions:delete_transaction', args=[transaction.id]))
    assert response.status_code == 302
    assert response.url == reverse('users:dashboard')
    assert not Transaction.objects.filter(id=transaction.id).exists()

def test_categories_view(client, user):
    client.login(username='testuser', password='12345')
    category = Category.objects.first()
    response = client.get(reverse('transactions:categories'))
    assert response.status_code == 200
    response_data = response.json()
    categories = serializers.deserialize('json', response_data['categories'])
    assert any(obj.object.name == 'Test Category' for obj in categories)

def test_manage_categories_view(client, user):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('transactions:manage_categories'))
    assert response.status_code == 200
    assert b'Test Category' in response.content
    response = client.post(reverse('transactions:manage_categories'), {'name': 'New Category'})
    assert response.status_code == 200
    # assert response.url == reverse('transactions:manage_categories')
    # assert Category.objects.filter(name='New Category').exists()

def test_delete_category_view(client, user):
    client.login(username='testuser', password='12345')
    category = Category.objects.create(name='New Category', user=user)
    response = client.post(reverse('transactions:delete_category', args=[category.id]))
    assert response.status_code == 302
    assert response.url == reverse('transactions:manage_categories')
    assert not Category.objects.filter(id=category.id).exists()

def test_transaction_list_view(client, user):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('transactions:transaction_list'))
    assert response.status_code == 200
    # Assert additional logic based on the response content or data returned from the view
    # For example, you can check if the response contains specific transaction data.
