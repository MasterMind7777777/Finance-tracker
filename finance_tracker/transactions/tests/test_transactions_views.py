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

@pytest.fixture
def user2(db):
    user = User.objects.create_user(username='testuser2', password='123456')
    category = Category.objects.create(name='Test Category2', user=user2)
    return user2

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

@pytest.mark.django_db
def test_add_transaction_view_with_invalid_data(client, user):
    client.login(username='testuser', password='12345')
    response = client.post(reverse('transactions:add_transaction'), {
        'title': '',  # Empty title
        'description': 'This is a test transaction.',
        'amount': 100.0,
        'category': 1,
        'date': '2023-07-01',
    })
    assert response.status_code == 200
    assert b"Invalid form submission." in response.content

@pytest.mark.django_db
def test_add_transaction_view_without_login(client):
    response = client.post(reverse('transactions:add_transaction'), {
        'title': 'Test Transaction',
        'description': 'This is a test transaction.',
        'amount': 100.0,
        'category': 1,
        'date': '2023-07-01',
    })
    assert 'login' in response.url  # Check that the user is redirected to the login page

@pytest.mark.django_db
def test_delete_transaction_view_with_other_user(client, user):
    other_user = User.objects.create_user(username='otheruser', password='12345')
    client.login(username='otheruser', password='12345')
    transaction = Transaction.objects.create(
        title='Test Transaction',
        description='This is a test transaction.',
        amount=100.0,
        category=Category.objects.first(),
        date=make_aware(datetime.datetime(2023, 7, 1)),
        user=user
    )
    response = client.post(reverse('transactions:delete_transaction', args=[transaction.id]))
    assert response.status_code == 403  # Check that the user gets a forbidden response

@pytest.mark.django_db
def test_transaction_detail_view(client, user):
    client.login(username='testuser', password='12345')
    transaction = Transaction.objects.create(
        title='Test Transaction',
        description='This is a test transaction.',
        amount=100.0,
        category=Category.objects.first(),
        date=make_aware(datetime.datetime(2023, 7, 1)),
        user=user
    )
    response = client.get(reverse('transactions:transaction_detail', args=[transaction.id]))
    assert response.status_code == 200
    assert b'Test Transaction' in response.content

@pytest.mark.django_db
def test_transaction_list_view_with_filters_and_sorting(client, user):
    client.login(username='testuser', password='12345')
    category = Category.objects.create(name='Test Category 2', user=user)
    transaction1 = Transaction.objects.create(
        title='Test Transaction 1',
        description='This is a test transaction.',
        amount=100.0,
        category=Category.objects.first(),
        date=make_aware(datetime.datetime(2023, 7, 1)),
        user=user
    )
    transaction2 = Transaction.objects.create(
        title='Test Transaction 2',
        description='This is another testtransaction.',
        amount=200.0,
        category=category,
        date=make_aware(datetime.datetime(2023, 7, 2)),
        user=user
    )
    
    # Test descending sorting
    response = client.get(reverse('transactions:transaction_list'), {
        'filter_by': 'category',
        'filter_value': 'Test Category 2',
        'sort_field': 'amount',
        'sort_order': 'desc',
    })
    assert response.status_code == 200
    assert b'Test Transaction 2' in response.content
    assert b'Test Transaction 1' not in response.content
    
    # Test ascending sorting
    response = client.get(reverse('transactions:transaction_list'), {
        'filter_by': 'category',
        'filter_value': 'Test Category 2',
        'sort_field': 'amount',
        'sort_order': 'asc',
    })
    assert response.status_code == 200
    
    # Check descending sorting
    transactions_descending = response.context['transactions']
    amounts_descending = [transaction.amount for transaction in transactions_descending]
    assert amounts_descending == sorted(amounts_descending, reverse=True)
    
    # Check ascending sorting
    response = client.get(reverse('transactions:transaction_list'), {
        'filter_by': 'category',
        'sort_field': 'amount',
        'sort_order': 'asc',
    })
    assert response.status_code == 200
    transactions_ascending = response.context['transactions']
    amounts_ascending = [transaction.amount for transaction in transactions_ascending]
    assert amounts_ascending == sorted(amounts_ascending)


@pytest.mark.django_db
def test_transaction_detail_view_with_subtransaction_creation(client, user):
    client.login(username='testuser', password='12345')
    transaction = Transaction.objects.create(
        title='Test Transaction',
        description='This is a test transaction.',
        amount=100.0,
        category=Category.objects.first(),
        date=make_aware(datetime.datetime(2023, 7, 1)),
        user=user
    )
    response = client.post(reverse('transactions:transaction_detail', args=[transaction.id]), {
        'title': 'Test Subtransaction',
        'description': 'This is a test subtransaction.',
        'amount': 50.0,
        'category': transaction.category.id,
        'date': '2023-07-01',
    })
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data['title'] == 'Test Subtransaction'
    assert Transaction.objects.filter(title='Test Subtransaction').exists()


# ToDo
# This feature will analyze the user's past transactions 
# and use in future(machine learning algorithms) it will give most used 
# transactions for now to predict future transactions. 
# It can be useful for users who want to automate their transaction recording process.
def test_transaction_recommendation_feature(client, user):
    client.force_login(user)
    response = client.post('/transactions/add/', {'category': 'Groceries', 'amount': 100})
    assert response.status_code == 200

    recommendations = client.get('/transactions/recommendations/')
    assert recommendations.status_code == 200
    assert 'Groceries' in [r['category'] for r in recommendations.context['recommendations']]