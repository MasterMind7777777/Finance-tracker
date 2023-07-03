import pytest
from transactions.models import Category, Transaction
from budgets.models import CategoryBudget
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_password():
    return 'strong-test-pass'

@pytest.fixture
def create_user(db, test_password):
    new_user = User.objects.create_user(username='user', password=test_password)
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
    budget = CategoryBudget.objects.create(user=create_user, category=create_category, budget_limit=500)
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
