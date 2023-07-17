import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_tracker.settings')

app = Celery('finance_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

CELERY_BEAT_SCHEDULE = {
    'apply-daily-recurring-transactions': {
        'task': 'transactions.tasks.apply_recurring_transactions_task',
        'schedule': crontab(minute=0, hour=0),  # Runs every day at midnight.
        'args': ('daily',)
    },
    'apply-weekly-recurring-transactions': {
        'task': 'transactions.tasks.apply_recurring_transactions_task',
        'schedule': crontab(minute=0, hour=0, day_of_week='monday'),  # Runs every Monday at midnight.
        'args': ('weekly',)
    },
    'apply-monthly-recurring-transactions': {
        'task': 'transactions.tasks.apply_recurring_transactions_task',
        'schedule': crontab(minute=0, hour=0, day_of_month='1'),  # Runs on the first day of every month at midnight.
        'args': ('monthly',)
    },
    'apply-yearly-recurring-transactions': {
        'task': 'transactions.tasks.apply_recurring_transactions_task',
        'schedule': crontab(minute=0, hour=0, day_of_month='1', month_of_year='1'),  # Runs on the first day of every year at midnight.
        'args': ('yearly',)
    },
}