import pytest
from transactions.models import Category, Transaction
from budgets.models import CategoryBudget
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.models import PushNotification
from decimal import Decimal


User = get_user_model()


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

def test_budget_alerts(client, create_user):
    client.force_login(create_user)
    # Create an instance of APIClient
    client = APIClient()

    # Force login using create_user
    client.force_authenticate(user=create_user)

    # Create a category
    category_data = {'name': 'Groceries', 'type': 'expense'}
    category_response = client.post(reverse('api_v1:category-list'), category_data, format='json')
    assert category_response.status_code == 201

    # Send a POST request to create a budget
    budget_data = {'category': category_response.data['id'], 'budget_limit': 100}
    budget_response = client.post(reverse('api_v1:budget-list'), budget_data, format='json')
    assert budget_response.status_code == 201

    # Send a POST request to add a transaction
    transaction_data = {'title': 'test transaction','category': category_response.data['id'], 'amount': 101}
    transaction_response = client.post(reverse('api_v1:transaction-list'), transaction_data, format='json')
    assert transaction_response.status_code == 201

    alerts = client.get(reverse('api_v1:budget-alerts'))
    print(alerts)
    assert alerts.status_code == 200
    assert 'Groceries' in alerts.json()['over_limit_categories']

def test_push_notifications_for_budget_alerts(client, create_user):
    client.force_login(create_user)
    # Create an instance of APIClient
    client = APIClient()

    # Force login using create_user
    client.force_authenticate(user=create_user)

    # Create a category
    category_data = {'name': 'Food', 'type': 'expense'}
    category_response = client.post(reverse('api_v1:category-list'), category_data, format='json')
    assert category_response.status_code == 201

    # Send a POST request to create a budget
    budget_data = {'category': category_response.data['id'], 'budget_limit': 100}
    budget_response = client.post(reverse('api_v1:budget-list'), budget_data, format='json')
    assert budget_response.status_code == 201

    # Send a POST request to add a transaction
    transaction_data = {'title': 'test transaction','category': category_response.data['id'], 'amount': 101}
    transaction_response = client.post(reverse('api_v1:transaction-list'), transaction_data, format='json')
    assert transaction_response.status_code == 201
    
    # Run the alerts view which generates the budget alerts
    response = client.get(reverse('api_v1:budget-alerts'))
    
    # Check if the alert is generated
    assert response.status_code == 200
    print(response.json())
    assert 'Food' in response.json()['over_limit_categories']
    
    # Now let's check if a push notification is generated for the alert
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
