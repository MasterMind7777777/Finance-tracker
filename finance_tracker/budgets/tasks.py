from celery import shared_task
from django.contrib.auth import get_user_model
from budgets.models import CategoryBudget, CustomBudgetAlert
from transactions.models import Transaction
from users.models import PushNotification
from django.db.models import Sum
from django.core.cache import cache
from celery.result import AsyncResult

User = get_user_model()

@shared_task()
def process_budget_alert(user_id, budget_id, total_spent):
    user = User.objects.get(id=user_id)
    budget = CategoryBudget.objects.get(id=budget_id)

    over_limit_categories = []
    custom_alerts = []

    if total_spent > budget.budget_limit:
        over_limit_categories.append(budget.category.name)
        PushNotification.objects.create(user=user, content='You have exceeded your budget limit for ' + budget.category.name)

    custom_alert = CustomBudgetAlert.objects.filter(budget=budget).first()
    if custom_alert and total_spent > custom_alert.threshold:
        custom_alerts.append(custom_alert.message)
        PushNotification.objects.create(user=user, content=custom_alert.message)

    result = {
        'over_limit_categories': over_limit_categories,
        'custom_alerts': custom_alerts
    }

    print(result)
    return result

@shared_task(bind=True)
def generate_budget_alerts(self, user_id):
    user = User.objects.get(id=user_id)
    budgets = CategoryBudget.objects.filter(user=user)
    over_limit_categories = []
    custom_alerts = []

    # Check if the results are already cached
    cache_key = f"alerts_result_{user_id}"
    process_tasks = cache.get(cache_key)

    if process_tasks is None:
        process_tasks = []
        for budget in budgets:
            total_spent = Transaction.objects.filter(user=user, category=budget.category).aggregate(Sum('amount'))['amount__sum'] or 0
            process_task = process_budget_alert.delay(user.id, budget.id, total_spent)
            process_tasks.append(process_task.id)  # Store the task ID

        # Store the task IDs in the cache

        cache.set(cache_key, process_tasks, timeout=None)

    response_data = {
            'over_limit_categories': over_limit_categories,
            'custom_alerts': custom_alerts
        }
    
    return response_data

def check_budget_alerts(user_id):
    cache_key = f"alerts_result_{user_id}"
    process_tasks = cache.get(cache_key)

    if process_tasks is None:
        return {'status': 'Error', 'message': 'No tasks found for this user.'}

    all_tasks_ready = all(AsyncResult(task_id).ready() for task_id in process_tasks)

    if all_tasks_ready:
        over_limit_categories = []
        custom_alerts = []

        results = [AsyncResult(task_id).result for task_id in process_tasks]
        for res in results:
            over_limit_categories.extend(res['over_limit_categories'])
            custom_alerts.extend(res['custom_alerts'])
        response_data = {
            'over_limit_categories': over_limit_categories,
            'custom_alerts': custom_alerts
        }

    return response_data