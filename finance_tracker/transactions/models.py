from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    EXPENSE = 'expense'
    INCOME = 'income'
    SAVING = 'saving'
    INVESTMENT = 'investment'
    
    CATEGORY_TYPES = [
        (EXPENSE, 'Expense'),
        (INCOME, 'Income'),
        (SAVING, 'Saving'),
        (INVESTMENT, 'Investment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='subcategories')

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Recurring Transaction {self.id}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)
    parent_transaction = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='sub_transactions')
    recurring_transaction = models.ForeignKey(RecurringTransaction, on_delete=models.CASCADE, null=True, blank=True)
    currency = models.CharField(choices=settings.CURRENCIES.items(), default='USD', max_length=3)

    def __str__(self):
        return f"Transaction {self.id}"


class TransactionSplit(models.Model):
    REQUEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ]
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_splits_made')
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_splits_received')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=REQUEST_STATUS_CHOICES, default='pending', max_length=10)

    class Meta:
        unique_together = ['requester', 'requestee', 'transaction']