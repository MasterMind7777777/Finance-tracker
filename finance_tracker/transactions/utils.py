import re
import time
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import ValidationError
from .models import Category
from django.db.models import Max
from .models import Transaction, RecurringTransaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from celery.result import AsyncResult
from .tasks import categorize_transaction_task, compare_spending_task, forecast_expenses_task
User = get_user_model()
import nltk

nltk.data.path.append('C:/projects/Finance-tracker/finance_tracker/nltk')
try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
except:
    nltk.download('stopwords', download_dir='C:/projects/Finance-tracker/finance_tracker/nltk')
    nltk.download('punkt', download_dir='C:/projects/Finance-tracker/finance_tracker/nltk')
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

class CategoryEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return str(obj)
        return super().default(obj)

def forecast_expenses(user_id):
    # The key is 'forecast_expenses_task' + user_id
    cache_key = f'forecast_expenses_task_{user_id}'
    task_id = cache.get(cache_key)
    
    if task_id is None:
        # The task has not been launched yet, so we do it and store the task id in cache
        result = forecast_expenses_task.delay(user_id)
        cache.set(cache_key, str(result.id))
        return {"status": "Pending"}
    else:
        # A task has been launched in the past, we check its status
        result = AsyncResult(task_id)
        if result.ready():
            # If the task is ready, we clear the cache and return the result
            cache.delete(cache_key)
            return {"status": "Complete", "result": result.get()}
        else:
            return {"status": "Pending"}

def categorize_transaction(transaction_id, user_id):
    cache_key = f"categorize_transaction_task_{transaction_id}_{user_id}"
    task_id = cache.get(cache_key)

    if not task_id:
        # Initiate the task and store its ID and status in the cache
        task = categorize_transaction_task.delay(transaction_id, user_id)
        task_id = task.id
        return {"status": "Pending"}
    else:
        # Check the status of the task
        task = AsyncResult(task_id)
        if task.ready():
            task_result = task.result
            if task_result['status'] == 'Pending':
                return {"status": "Pending"}
            category = Category.objects.get(pk=task_result['best_matching_category'])
            transaction = Transaction.objects.get(pk=transaction_id)
            transaction.category = category
            transaction.save()
            cache.delete(cache_key)
            return task_result
        else:
            return {"status": "Pending"}

def apply_recurring_transactions():
    # Current date
    current_date = timezone.now().date()

    # Retrieve the latest transaction dates for each recurring transaction
    latest_transaction_dates = Transaction.objects.filter(
        recurring_transaction__isnull=False,
        date__date__lt=current_date
    ).values('recurring_transaction').annotate(latest_date=Max('date__date'))

    # Get the recurring transactions for the latest dates
    recurring_transactions = RecurringTransaction.objects.filter(
        pk__in=[item['recurring_transaction'] for item in latest_transaction_dates]
    )

    # Create a list of transactions to create
    transactions_to_create = []

    for transaction_date in latest_transaction_dates:
        recurring_transaction = next(
            rt for rt in recurring_transactions if rt.pk == transaction_date['recurring_transaction']
        )
        latest_date = transaction_date['latest_date']

        if recurring_transaction.frequency == 'daily' and (current_date - latest_date).days >= 1:
            transactions_to_create.append(create_new_transaction(recurring_transaction))
        elif recurring_transaction.frequency == 'weekly' and (current_date - latest_date).days >= 7:
            transactions_to_create.append(create_new_transaction(recurring_transaction))
        elif recurring_transaction.frequency == 'monthly' and (current_date.month != latest_date.month or current_date.year != latest_date.year):
            transactions_to_create.append(create_new_transaction(recurring_transaction))
        elif recurring_transaction.frequency == 'yearly' and current_date.year != latest_date.year:
            transactions_to_create.append(create_new_transaction(recurring_transaction))

    # Bulk create the new transactions
    Transaction.objects.bulk_create(transactions_to_create)

def create_new_transaction(recurring_transaction):
    # Create a new Transaction instance with the properties from the recurring transaction
    return Transaction(
        user=recurring_transaction.user,
        title=f'Recurring Transaction {recurring_transaction.id}',
        amount=recurring_transaction.amount,
        category=recurring_transaction.category,
        date=timezone.now(),
        recurring_transaction=recurring_transaction
    )

def compare_spending(user_id, friends_ids, category_id, period_days=30):
    cache_key = f'compare_spending_task_{user_id}_{category_id}'
    task_id = cache.get(cache_key)
    
    if task_id is None:
        result = compare_spending_task.delay(user_id, friends_ids, category_id, period_days)
        cache.set(cache_key, str(result.id))
        return {"status": "Pending"}
    else:
        result = AsyncResult(task_id)
        if result.ready():
            if result.result['status'] == 'Pending':
                return {"status": "Pending"}
            elif result.result['status'] == 'Error':
                cache.delete(cache_key)
                raise ValidationError(result.result['message'])
            cache.delete(cache_key)
            return result.get()
        else:
            return {"status": "Pending"}