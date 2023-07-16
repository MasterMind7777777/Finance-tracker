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
    print(task_id)
    if task_id is None:
        # The task has not been launched yet, so we do it and store the task id in cache
        result = forecast_expenses_task.delay(user_id)
        cache.set(cache_key, result.id)
        return {"status": "Pending"}
    else:
        # A task has been launched in the past, we check its status
        result = AsyncResult(task_id)
        print(result.ready())
        if result.ready():
            # If the task is ready, we clear the cache and return the result
            cache.delete(cache_key)
            return {"status": "Complete", "result": result.result}
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