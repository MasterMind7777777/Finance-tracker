import csv
import datetime
from decimal import Decimal
import pytest
import json
from django.utils.timezone import make_aware
from django.core import serializers
from django.urls import reverse
from django.test import Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from transactions.models import TransactionSplit
from transactions.utils import categorize_transaction, apply_recurring_transactions
from transactions.models import Transaction, Category
from rest_framework.test import APIClient
from rest_framework import status
import calendar
from datetime import timedelta, datetime
from django.utils import timezone
import random
from transactions.utils import forecast_expenses
import os
from django.test import override_settings
from celery import current_app

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', password='12345')
    return user

@pytest.fixture
def user1(db):
    user = User.objects.create_user(username='testuser1', password='12345')
    return user

@pytest.fixture
def user2(db):
    user = User.objects.create_user(username='testuser2', password='123456')
    return user

@pytest.fixture
def user3(db):
    user = User.objects.create_user(username='testuser3', password='123456')
    return user

@pytest.fixture
def category1(db, user):
    category = Category.objects.create(name='Test Category3', user=user, type=Category.EXPENSE)
    return category

@pytest.fixture
def category2(db, user):
    category = Category.objects.create(name='Test Category4', user=user, type=Category.EXPENSE)
    return category

@pytest.fixture
def category3(db, user2):
    category = Category.objects.create(name='Test Category5', user=user2, type=Category.EXPENSE)
    return category

def test_add_transaction_view(client, user, category1):
    client.login(username='testuser', password='12345')
    category = Category.objects.first()
    transaction_date = make_aware(datetime(2023, 7, 1))  # Add the appropriate timezone information
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

def test_delete_transaction_view(client, user, category1):
    client.login(username='testuser', password='12345')
    transaction_date = make_aware(datetime(2023, 7, 1))  # Add the appropriate timezone information
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

def test_categories_view(client, user, category1):
    client.login(username='testuser', password='12345')
    category = Category.objects.first()
    response = client.get(reverse('transactions:categories'))
    assert response.status_code == 200
    response_data = response.json()
    categories = serializers.deserialize('json', response_data['categories'])
    assert any(obj.object.name == 'Test Category3' for obj in categories)

def test_manage_categories_view(client, user, category1):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('transactions:manage_categories'))
    assert response.status_code == 200
    assert b'Test Category3' in response.content
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
        date=make_aware(datetime(2023, 7, 1)),
        user=user
    )
    response = client.post(reverse('transactions:delete_transaction', args=[transaction.id]))
    assert response.status_code == 403  # Check that the user gets a forbidden response

@pytest.mark.django_db
def test_transaction_detail_view(client, user, category1):
    client.login(username='testuser', password='12345')
    transaction = Transaction.objects.create(
        title='Test Transaction',
        description='This is a test transaction.',
        amount=100.0,
        category=Category.objects.first(),
        date=make_aware(datetime(2023, 7, 1)),
        user=user
    )
    response = client.get(reverse('transactions:transaction_detail', args=[transaction.id]))
    assert response.status_code == 200
    assert b'Test Transaction' in response.content

@pytest.mark.django_db
def test_transaction_list_view_with_filters_and_sorting(client, user, category1):
    client.login(username='testuser', password='12345')
    category = Category.objects.create(name='Test Category 2', user=user)
    transaction1 = Transaction.objects.create(
        title='Test Transaction 1',
        description='This is a test transaction.',
        amount=100.0,
        category=category1,
        date=make_aware(datetime(2023, 7, 1)),
        user=user
    )
    transaction2 = Transaction.objects.create(
        title='Test Transaction 2',
        description='This is another testtransaction.',
        amount=200.0,
        category=category,
        date=make_aware(datetime(2023, 7, 2)),
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
def test_transaction_detail_view_with_subtransaction_creation(client, user, category1):
    client.login(username='testuser', password='12345')
    transaction = Transaction.objects.create(
        title='Test Transaction',
        description='This is a test transaction.',
        amount=100.0,
        category=Category.objects.first(),
        date=make_aware(datetime(2023, 7, 1)),
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

def test_transaction_recommendation_feature(client, user):
    client = APIClient()
    client.force_authenticate(user=user)

    # Create a category
    categories_data = [
        {'name': 'Groceries', 'type': 'expense'},
        {'name': 'test', 'type': 'expense'}
        ]
    categories_ids = []
    for category_data in categories_data:
        category_response = client.post(reverse('api_v1:category-list'), category_data, format='json')
        assert category_response.status_code == 201
        categories_ids.append(category_response.data['id'])  # Store category id

    transaction_ids = []  # Keep track of created transaction ids

    # Create multiple transactions
    transactions_data = [
        {'title': 'Transaction 1', 'category': categories_ids[0], 'amount': 100},
        {'title': 'Transaction 2', 'category': categories_ids[1], 'amount': 200},
        {'title': 'Transaction 3', 'category': categories_ids[1], 'amount': 150},
        # Add more transactions as needed
    ]

    for transaction_data in transactions_data:
        transaction_response = client.post(reverse('api_v1:transaction-list'), transaction_data, format='json')
        assert transaction_response.status_code == 201
        transaction_ids.append(transaction_response.data['id'])  # Store transaction id


    # Check recommendations with different num_recommendations values
    num_recommendations_values = [2, 3, 5]  # Example values
    for num_recommendations in num_recommendations_values:
        recommendations_url = reverse('api_v1:transaction-recommendations') + f'?num_recommendations={num_recommendations}'
        recommendations_response = client.get(recommendations_url)
        assert recommendations_response.status_code == 200
        assert all(transaction['id'] in transaction_ids for transaction in recommendations_response.data['recommendations'])
        assert recommendations_response.data['most_used_category'] == categories_ids[1]  # Ensure the 'most_used_category' matches the category used




@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
@pytest.mark.django_db
def test_expense_forecasting(client, user):
    client = APIClient()
    client.force_authenticate(user=user)
    current_app.conf.task_store_eager_result = True

    # Create transactions within the current month at random day deltas
    today = timezone.now()
    start_of_month = timezone.make_aware(datetime(today.year, today.month, 1))

    _, days_in_current_month = calendar.monthrange(today.year, today.month)
    
    for _ in range(3):
        random_day_delta = random.randint(1, days_in_current_month)
        random_date = start_of_month + timedelta(days=random_day_delta)
        random_date_aware = timezone.make_aware(datetime(random_date.year, random_date.month, random_date.day))
        Transaction.objects.create(user=user, amount=random.randint(500, 2000), date=random_date_aware)

    # Calculate the total expenses and the average daily spending
    transactions_within_month = Transaction.objects.filter(user=user, date__gte=start_of_month)
    total_expenses = sum(transaction.amount for transaction in transactions_within_month)

    average_daily_spending = total_expenses / ((today - start_of_month).days + 1) 

    # Calculate the forecasted expenses for the current month
    forecasted_expenses = average_daily_spending * days_in_current_month

    # Get the forecasted expenses using the function
    forecast_data = forecast_expenses(user.id)

    assert forecast_data["status"] == "Pending"

    # Here you would usually wait for the task to be completed before calling forecast_expenses again. 
    # But for the test, let's assume that the task is completed instantly.

    forecast_data = forecast_expenses(user.id)

    assert forecast_data["status"] == "Complete"

    calculated_forecast = forecast_data["result"]

    # Assert that the calculated forecast matches the expected result
    assert calculated_forecast == pytest.approx(forecasted_expenses, abs=0.01)

    # Get the forecasted expenses using api
    response = client.get(reverse('api_v1:transaction-forecast-expenses'))
    forecast_data = response.json()

    assert forecast_data["status"] == "Pending"

    # Here you would usually wait for the task to be completed before calling the API endpoint again. 
    # But for the test, let's assume that the task is completed instantly.

    response = client.get(reverse('api_v1:transaction-forecast-expenses'))
    forecast_data = response.json()

    assert forecast_data["status"] == "Complete"

    calculated_forecast = forecast_data["result"]

    # Assert that the calculated forecast matches the expected result
    forecasted_expenses_decimal = Decimal(forecasted_expenses)
    assert calculated_forecast == pytest.approx(forecasted_expenses_decimal, abs=Decimal(0.01))

@pytest.mark.django_db
def test_automatic_categorization_of_transactions():
    # create test user
    user = User.objects.create(username="test_user", password="test_password")

    # create categories
    categories = [
        Category.objects.create(user=user, name="Subscriptions"),
        Category.objects.create(user=user, name="Food"),
        Category.objects.create(user=user, name="Transportation"),
    ]

    # create categorized transactions
    Transaction.objects.create(user=user, title="Magazine subscription", amount=8, category=categories[0], description="Monthly subscription for a popular magazine.")
    Transaction.objects.create(user=user, title="Coffee shop", amount=5, category=categories[1], description="Bought a cup of coffee at a local café.")
    Transaction.objects.create(user=user, title="Bus fare", amount=3, category=categories[2], description="Paid for a bus ride to the city center.")
    Transaction.objects.create(user=user, title="Online streaming service", amount=12, category=categories[0], description="Monthly subscription for an online streaming service.")
    Transaction.objects.create(user=user, title="Grocery shopping", amount=40, category=categories[1], description="Purchased groceries for the week.")
    Transaction.objects.create(user=user, title="Gas station", amount=25, category=categories[2], description="Filled up the car's fuel tank at a nearby gas station.")
    Transaction.objects.create(user=user, title="Dinner at a restaurant", amount=50, category=categories[1], description="Enjoyed a delicious dinner at a fancy restaurant.")
    Transaction.objects.create(user=user, title="Movie tickets", amount=15, category=categories[2], description="Bought tickets for a movie night with friends.")
    Transaction.objects.create(user=user, title="Gym membership", amount=60, category=categories[0], description="Paid for a monthly gym membership.")
    Transaction.objects.create(user=user, title="Lunch at a cafe", amount=10, category=categories[1], description="Had a quick lunch at a cozy café.")
    Transaction.objects.create(user=user, title="Taxi ride", amount=20, category=categories[2], description="Took a taxi to the airport.")
    Transaction.objects.create(user=user, title="Online music streaming", amount=9, category=categories[0], description="Monthly subscription for a music streaming platform.")
    Transaction.objects.create(user=user, title="Fast food", amount=8, category=categories[1], description="Ordered fast food for dinner.")
    Transaction.objects.create(user=user, title="Metro fare", amount=4, category=categories[2], description="Paid for a metro ride across the city.")
    Transaction.objects.create(user=user, title="Online video streaming", amount=11, category=categories[0], description="Monthly subscription for a video streaming service.")
    Transaction.objects.create(user=user, title="Grocery shopping", amount=35, category=categories[1], description="Bought groceries and household essentials.")
    Transaction.objects.create(user=user, title="Car maintenance", amount=50, category=categories[2], description="Got the car serviced and oil changed.")
    Transaction.objects.create(user=user, title="Breakfast at a cafe", amount=7, category=categories[1], description="Enjoyed a hearty breakfast at a local café.")
    Transaction.objects.create(user=user, title="Train ticket", amount=15, category=categories[2], description="Purchased a train ticket for a weekend trip.")
    Transaction.objects.create(user=user, title="Online magazine subscription", amount=6, category=categories[0], description="Subscribed to an online magazine for the latest news and articles.")


    # create an uncategorized transaction
    uncategorized_transaction = Transaction.objects.create(user=user, title="Subscribe to a streamer", description="Yearly subscription for my fevorite stremer", amount=10)

    # categorize the transaction automatically
    found_category = categorize_transaction(uncategorized_transaction.id, user)
    uncategorized_transaction.refresh_from_db()

    # check if the transaction has been categorized
    assert uncategorized_transaction.category is not None
    assert uncategorized_transaction.category.name == "Subscriptions"  # Assuming Subscribe to a streamer falls under "Subscriptions" category

        # create an uncategorized transaction
    uncategorized_transaction2 = Transaction.objects.create(user=user, title="Subscribe to a streamer", description="Yearly subscription for my favorite streamer", amount=10)

    # create the APIClient instance
    client = APIClient()

    # authenticate the client as the test user
    client.force_authenticate(user=user)

    # construct the URL for the assign_category endpoint
    url = reverse('api_v1:transaction-assign_category', kwargs={'transaction_id': uncategorized_transaction2.id})

    # make a POST request to assign the category
    response = client.post(url)

    # check the response status code
    assert response.status_code == 200

    # refresh the transaction from the database
    uncategorized_transaction2.refresh_from_db()

    # check if the transaction has been categorized
    assert uncategorized_transaction2.category is not None
    assert uncategorized_transaction2.category.name == "Subscriptions"

def test_recurring_transactions(user):
    category = Category.objects.create(name="rent", user=user)
    client = APIClient()
    client.force_authenticate(user=user)

    # Create a new recurring transaction
    recurring_transaction_data = {
        'user': user.id,
        'title': 'pay for home',
        'amount': 500,
        'category': category.id,
        'is_recurring': True,
        'recurring_transaction_meta': {
            'frequency': 'monthly',
            'start_date': timezone.now().date().isoformat(),  # assuming it starts today
            'end_date': (timezone.now() + timedelta(days=30)).date().isoformat()  # and ends in a month
        }
    }

    url = reverse('api_v1:transaction-list')
    response = client.post(url, recurring_transaction_data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    recurring_transaction_id = response.data['id']

    # Simulate the application of recurring transactions
    apply_recurring_transactions()

    response = client.get(url, {'user': user.id, 'category': category.id, 'amount': 500}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['recurring_transaction'] == recurring_transaction_id

    frequency_choices = ['daily', 'weekly', 'monthly', 'yearly']
    start_date = timezone.now().date()  # Start from today


    # Initialize a variable to count the transactions
    transaction_count = 0
    # Test different frequency choices
    for frequency in frequency_choices:
        recurring_transaction_data['recurring_transaction_meta']['frequency'] = frequency
        recurring_transaction_data['recurring_transaction_meta']['start_date'] = start_date.isoformat()

        # Adjust end_date based on frequency
        if frequency == 'daily':
            end_date = start_date + timedelta(days=7)  # One week
        elif frequency == 'weekly':
            end_date = start_date + timedelta(weeks=4)  # Four weeks
        elif frequency == 'monthly':
            end_date = start_date + timedelta(days=365)  # One year
        else:  # 'yearly'
            end_date = start_date + timedelta(days=365 * 5)  # Five years

        recurring_transaction_data['recurring_transaction_meta']['end_date'] = end_date.isoformat()

        response = client.post(url, recurring_transaction_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

        # Simulate the application of recurring transactions
        apply_recurring_transactions()

        response = client.get(url, {'user': user.id, 'category': category.id, 'amount': 500}, format='json')
        assert response.status_code == status.HTTP_200_OK

        # Increment the transaction count by the number of transactions in the response
        transaction_count += len(response.data)

        assert response.data[0]['recurring_transaction'] == recurring_transaction_id


        # Test recurring transactions with different start and end dates
        recurring_transaction_data['recurring_transaction_meta']['frequency'] = 'monthly'

        # Change start_date to one month before today
        recurring_transaction_data['recurring_transaction_meta']['start_date'] = (timezone.now() - timedelta(days=30)).date().isoformat()

        # Change end_date to one month after today
        recurring_transaction_data['recurring_transaction_meta']['end_date'] = (timezone.now() + timedelta(days=60)).date().isoformat()

        response = client.post(url, recurring_transaction_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

def test_transactions_bulk_upload(client, user, category1, category2, category3):
    client.force_login(user)

    # Get the current directory
    current_directory = os.getcwd()

    # Specify the relative path from the current directory
    relative_path = 'transactions/tests/test_transactions.csv'

    # Join the current directory path with the relative path
    file_path = os.path.join(current_directory, relative_path)

    url = reverse('api_v1:transaction-bulk-upload')  # Replace `api_v1` with the actual API URL namespace
    with open(file_path, 'rb') as file:
        # Create a SimpleUploadedFile object from the file
        uploaded_file = SimpleUploadedFile('test_file_name', file.read(), content_type='text/csv')
        response = client.post(url, {'file': uploaded_file})
    
    print(response.json())
    
    assert response.status_code == 200
    assert Transaction.objects.filter(user=user).count() > 0

def test_multiple_currencies(client, user, category1):
    client.force_login(user)
    url = reverse('api_v1:transaction-list')  # Assuming 'transaction-list' is the URL name for the TransactionViewSet
    data = {'title': 'test title', 'amount': 100, 'category': 1, 'currency': 'EUR'}
    response = client.post(url, data)
    assert response.status_code == 201
    assert Transaction.objects.filter(user=user, amount=100, category=1, currency='EUR').exists()

def test_transaction_splitting(client, user, user1, user2, user3, category1):
    client.force_login(user)
    transaction = Transaction.objects.create(user=user, title="Restaurant diner", amount=250, category=category1)
    url = reverse('api_v1:transaction-split-transaction', kwargs={'pk': transaction.id})
    data = {'splits': [{'user': user2.id, 'amount': 50}, {'user': user1.id, 'amount': 60}]}
    json_data = json.dumps(data)
    response = client.post(url, json_data, content_type='application/json')
    assert response.status_code == 201
    assert TransactionSplit.objects.filter(requester=user, requestee=user2, transaction=transaction, amount=50).exists()
    response = response.json()
    requestees = [3,2]
    amounts = [50,60]
    for inx, split in enumerate(response):
        assert split['requester'] == 1
        assert split['transaction'] == 1
        assert split['status'] == 'pending'
        assert split['requestee'] == requestees[inx]
        assert split['amount'] == amounts[inx]
    
    # Accept the transaction splits
    client.force_login(user2)
    split_url = reverse('api_v1:transaction_split-accept', kwargs={'pk': response[0]['id']})
    accept_response = client.put(split_url)
    assert accept_response.status_code == 200
    assert accept_response.json()['status'] == 'Transaction split accepted'
        
    # Verify if the original transaction amount is reduced
    transaction.refresh_from_db()
    assert transaction.amount == 200

    client.force_login(user)
    transaction = Transaction.objects.create(user=user, title="Restaurant diner 2", amount=350, category=category1)
    url = reverse('api_v1:transaction-split-transaction', kwargs={'pk': transaction.id})
    data = {'splits': [{'user': user2.id, 'amount': 60}, {'user': user1.id, 'amount': 70}]}
    json_data = json.dumps(data)
    response = client.post(url, json_data, content_type='application/json')
    assert response.status_code == 201
    response = response.json()
    assert TransactionSplit.objects.filter(requester=user, requestee=user2, transaction=transaction, amount=60).exists()
    
    client.force_login(user2)
    print(response[0]['id'])
    split_url = reverse('api_v1:transaction_split-decline', kwargs={'pk': response[0]['id']})
    decline_response = client.put(split_url)
    assert decline_response.status_code == 200
    assert decline_response.json()['status'] == 'Transaction split declined'



