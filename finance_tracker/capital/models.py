from django.db import models
from django.utils import timezone
from transactions.models import Transaction, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class SavingGoal(models.Model):
    creator = models.ForeignKey(User, related_name='created_goals', on_delete=models.CASCADE, null=True)
    users = models.ManyToManyField(User, related_name='shared_goals')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    target_date = models.DateField(null=True, blank=True)
    categories = models.ManyToManyField(Category, limit_choices_to={'type': Category.SAVING})

    def __str__(self):
        return f"{self.name} (Goal: {self.target_amount})"

    @property
    def current_amount(self):
        related_transactions = Transaction.objects.filter(user__in=self.users.all(), category__in=self.categories.all())
        return sum(trans.amount for trans in related_transactions if trans.date <= timezone.now())
