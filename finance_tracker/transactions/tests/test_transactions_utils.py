import pytest
from datetime import timedelta
from django.utils import timezone
from transactions.models import Transaction
import calendar
import random
from transactions.utils import forecast_expenses
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_expense_forecasting():
    # Create a user
    user = User.objects.create_user(username='testuser', password='12345')

    # Create transactions within the current month at random day deltas
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    _, days_in_current_month = calendar.monthrange(today.year, today.month)
    
    for _ in range(3):
        random_day_delta = random.randint(1, days_in_current_month)
        random_date = start_of_month + timedelta(days=random_day_delta)
        aware_datetime = timezone.make_aware(timezone.datetime.combine(random_date, timezone.datetime.min.time()))
        Transaction.objects.create(user=user, amount=random.randint(500, 2000), date=aware_datetime)

    # Calculate the total expenses and the average daily spending
    transactions_within_month = Transaction.objects.filter(user=user, date__gte=start_of_month)
    total_expenses = sum(transaction.amount for transaction in transactions_within_month)

    average_daily_spending = total_expenses / ((today - start_of_month).days + 1) 
    print(average_daily_spending)

    # Calculate the forecasted expenses for the current month
    forecasted_expenses = average_daily_spending * days_in_current_month

    # Get the forecasted expenses using the function
    calculated_forecast = forecast_expenses(user)

    # Assert that the calculated forecast matches the expected result
    assert calculated_forecast == pytest.approx(forecasted_expenses, abs=0.01)
