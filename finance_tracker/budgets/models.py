from django.db import models
from transactions.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()

class CategoryBudget(models.Model):
    user = models.ManyToManyField(User) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        user_names = ', '.join([user.username for user in self.user.all()])
        return f'{user_names} - {self.category.name}'