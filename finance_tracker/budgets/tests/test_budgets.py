import time
import pytest
from transactions.models import Category, Transaction
from budgets.models import CategoryBudget, CustomBudgetAlert
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.models import PushNotification
from decimal import Decimal
from django.test import override_settings
from unittest.mock import patch
from django.core.cache import cache
from celery import current_app

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()

@pytest.fixture
def test_password():
    return 'strong-test-pass'

@pytest.fixture
def create_user(db, test_password):
    new_user = User.objects.create_user(username='user', password=test_password)
    return new_user

@pytest.fixture
def create_user2(db, test_password):
    new_user = User.objects.create_user(username='user2', password=test_password)
    return new_user

@pytest.fixture
def create_category(db, create_user):
    category = Category.objects.create(user=create_user, name='Test Category', type=Category.EXPENSE)
    return category

@pytest.fixture
def create_transaction(db, create_user, create_category):
    transaction = Transaction.objects.create(user=create_user, title='Test Transaction', description='Test', amount=100, category=create_category)
    return transaction

@pytest.fixture
def create_budget(db, create_user, create_category):
    budget = CategoryBudget.objects.create(category=create_category, budget_limit=500)
    budget.user.add(create_user)
    return budget

def test_budget_overview(client, create_user, create_category, create_transaction, create_budget):
    client.login(username='user', password='strong-test-pass')

    url = reverse('budgets:budget_overview')
    response = client.get(url)

    assert response.status_code == 200
    assert 'total_income' in response.context
    assert 'total_expenses' in response.context
    assert 'current_balance' in response.context
    assert 'category_budgets' in response.context
    assert 'form' in response.context
    assert 'user_currency' in response.context
    assert 'categories' in response.context


def test_delete_budget(client, create_user, create_category, create_budget):
    client.login(username='user', password='strong-test-pass')

    url = reverse('budgets:delete_budget', kwargs={'budget_id': create_budget.id})
    response = client.post(url)

    assert response.status_code == 302
    assert CategoryBudget.objects.filter(id=create_budget.id).count() == 0

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_custom_budget_alerts(client, create_user, create_category):
    client.force_login(create_user)
    client = APIClient()
    client.force_authenticate(user=create_user)

    current_app.conf.task_store_eager_result = True

    category_budget = CategoryBudget.objects.create(category=create_category, budget_limit=100.0)
    category_budget.user.add(create_user)

    alert_data = {'threshold': 75, 'message': 'Custom alert message'}
    alert_response = client.post(reverse('api_v1:budget-create-custom-alert', kwargs={'pk': category_budget.id}), alert_data, format='json')
    assert alert_response.status_code == 201
    assert CustomBudgetAlert.objects.filter(budget__user=create_user, budget__id=1).exists()
    assert CustomBudgetAlert.objects.get(budget__user=create_user, budget__id=1).threshold == 75

    # Assuming there is a transaction that causes the threshold to be exceeded
    Transaction.objects.create(title='Test Transaction 1', user=create_user, amount=76.0, category=create_category)

    alert_task_response = client.get(reverse('api_v1:budget-alerts'))
    assert alert_task_response.status_code == 202
    alert_task_response = alert_task_response.json()
    assert alert_task_response['status'] == 'Pending'

    alert_task_response = client.get(reverse('api_v1:budget-alerts'))
    assert alert_task_response.status_code == 200
    alert_task_response = alert_task_response.json()
    assert alert_task_response['status'] == 'Complete'

    result = alert_task_response['result']

    assert 'Custom alert message' in result['custom_alerts']
    assert not result['over_limit_categories']

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_push_notifications_for_budget_alerts(client, create_user):
    client.force_login(create_user)
    client = APIClient()
    client.force_authenticate(user=create_user)

    current_app.conf.task_store_eager_result = True

    category_data = {'name': 'Food', 'type': 'expense'}
    category_response = client.post(reverse('api_v1:category-list'), category_data, format='json')
    assert category_response.status_code == 201

    budget_data = {'category': category_response.data['id'], 'budget_limit': 100}
    budget_response = client.post(reverse('api_v1:budget-list'), budget_data, format='json')
    assert budget_response.status_code == 201

    transaction_data = {'title': 'test transaction','category': category_response.data['id'], 'amount': 101}
    transaction_response = client.post(reverse('api_v1:transaction-list'), transaction_data, format='json')
    assert transaction_response.status_code == 201

    alert_task_response = client.get(reverse('api_v1:budget-alerts'))
    assert alert_task_response.status_code == 202
    alert_task_response = alert_task_response.json()
    assert alert_task_response['status'] == 'Pending'

    alert_task_response = client.get(reverse('api_v1:budget-alerts'))
    assert alert_task_response.status_code == 200
    alert_task_response = alert_task_response.json()
    assert alert_task_response['status'] == 'Complete'

    result = alert_task_response['result']

    assert 'Food' in result['over_limit_categories']

    push_notifications = PushNotification.objects.filter(user=create_user)
    assert len(push_notifications) == 1
    assert push_notifications[0].content == 'You have exceeded your budget limit for Food'

def test_category_budget(create_user, create_user2):
    # Create an instance of APIClient
    client = APIClient()

    # Force login using create_user
    client.force_authenticate(user=create_user)

    # Create a category
    category = Category.objects.create(name='Test Category', user=create_user, type=Category.EXPENSE)

    # Create a CategoryBudget
    category_budget = CategoryBudget.objects.create(category=category, budget_limit=1000.0)
    user1 = create_user
    user2 = create_user2
    category_budget.user.add(user1, user2)

    # Add transactions to the category budget
    transactions = [
        Transaction.objects.create(title='Test Transaction 1', user=user1, amount=200.0, category=category),
        Transaction.objects.create(title='Test Transaction 2', user=user1, amount=150.0, category=category),
        Transaction.objects.create(title='Test Transaction 3', user=user2, amount=250.0, category=category),
    ]

    # Fetch transactions for the category
    response = client.get(reverse('api_v1:transaction-list'), {'category_id': category.id})
    assert response.status_code == 200
    assert len(response.data) == 3  # Check that all three transactions are fetched

    # Check the properties of each transaction
    for i, transaction in enumerate(transactions):
        assert response.data[i]['title'] == transaction.title
        assert Decimal(response.data[i]['amount']) == transaction.amount

    # Calculate the remaining budget
    spent_amount = sum(Decimal(t.amount) for t in transactions)
    remaining_budget = Decimal(category_budget.budget_limit) - spent_amount

    assert remaining_budget == Decimal(400.0)  # The remaining budget after all three transactions
