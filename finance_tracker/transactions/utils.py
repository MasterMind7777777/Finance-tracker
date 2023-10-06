from django.core.serializers.json import DjangoJSONEncoder
from django.forms import ValidationError
from .models import Category
from .models import Transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from celery.result import AsyncResult
from .tasks import (
    categorize_transaction_task,
    compare_spending_task,
    forecast_expenses_task,
    apply_recurring_transactions_task,
)
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


class CategoryEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return str(obj)
        return super().default(obj)


def forecast_expenses(user_id):
    logger.info("Forecasting expenses for user_id %s", user_id)
    # The key is 'forecast_expenses_task' + user_id
    cache_key = f"forecast_expenses_task_{user_id}"
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
    logger.info(
        "Categorizing transaction %s for user_id %s", transaction_id, user_id
    )
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
            if task_result["status"] == "Pending":
                return {"status": "Pending"}
            try:
                category = Category.objects.get(
                    pk=task_result["best_matching_category"]
                )
            except Category.DoesNotExist:
                logger.error(
                    "Category with pk %s does not exist.",
                    task_result["best_matching_category"],
                )
                return {"status": "Error", "error": "Category does not exist"}
            transaction = Transaction.objects.get(pk=transaction_id)
            transaction.category = category
            transaction.save()
            cache.delete(cache_key)
            return task_result
        else:
            return {"status": "Pending"}


def apply_recurring_transactions(frequency):
    logger.info("Applying recurring transactions with frequency %s", frequency)
    task_id = apply_recurring_transactions_task.delay(frequency)
    return {"status": "Pending", "task_id": task_id}


def create_new_transaction(recurring_transaction):
    logger.info(
        "Creating new transaction for recurring_transaction %s",
        recurring_transaction.id,
    )
    # Create a new Transaction instance with the properties from the recurring transaction
    return Transaction(
        user=recurring_transaction.user,
        title=f"Recurring Transaction {recurring_transaction.id}",
        amount=recurring_transaction.amount,
        category=recurring_transaction.category,
        date=timezone.now(),
        recurring_transaction=recurring_transaction,
    )


def compare_spending(user_id, friends_ids, category_id, period_days=30):
    logger.info(
        "Comparing spending for user_id %s, category_id %s, period_days %s",
        user_id,
        category_id,
        period_days,
    )
    cache_key = f"compare_spending_task_{user_id}_{category_id}"
    task_id = cache.get(cache_key)

    if task_id is None:
        result = compare_spending_task.delay(
            user_id, friends_ids, category_id, period_days
        )
        cache.set(cache_key, str(result.id))
        return {"status": "Pending"}
    else:
        result = AsyncResult(task_id)
        if result.ready():
            if result.result["status"] == "Pending":
                return {"status": "Pending"}
            elif result.result["status"] == "Error":
                cache.delete(cache_key)
                raise ValidationError(result.result["message"])
            cache.delete(cache_key)
            return result.get()
        else:
            return {"status": "Pending"}
