from django.core.serializers.json import DjangoJSONEncoder
from .models import Category
from django.db.models import Sum, F
import calendar
from datetime import timedelta, timezone, datetime, date
from .models import Transaction

class CategoryEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return str(obj)
        return super().default(obj)

def forecast_expenses(user):
    today = date.today()
    start_of_month = today.replace(day=1)

    # Calculate the total number of days in the month
    total_days_in_month = calendar.monthrange(today.year , today.month)[1]

    # Calculate the actual number of days that have passed in the current month
    days_passed = (today - start_of_month).days + 1

    expenses = Transaction.objects.filter(user=user, date__gte=start_of_month).aggregate(total_expenses=Sum('amount'))
    total_expenses = expenses['total_expenses'] or 0

    # Calculate the average daily expenses
    avg_daily_expenses = total_expenses / days_passed
    print(avg_daily_expenses)

    # Calculate the forecasted expenses for the remaining days of the month
    forecast_next_month = avg_daily_expenses * total_days_in_month

    return forecast_next_month