from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    EXPENSE = 'expense'
    INCOME = 'income'
    CATEGORY_TYPES = [
        (EXPENSE, 'Expense'),
        (INCOME, 'Income'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)
    parent_transaction = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='sub_transactions')

    def __str__(self):
        return self.description
