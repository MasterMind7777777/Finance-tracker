from django.contrib import admin
from .models import CategoryBudget

@admin.register(CategoryBudget)
class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'budget_limit')
    list_filter = ('user', 'category')
    search_fields = ('user__username', 'category__name')
