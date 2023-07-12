from django.contrib import admin
from .models import CategoryBudget

@admin.register(CategoryBudget)
class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ('get_usernames', 'category', 'budget_limit')
    list_filter = ('user', 'category')
    search_fields = ('user__username', 'category__name')

    def get_usernames(self, obj):
        return ', '.join([user.username for user in obj.user.all()])
    
    get_usernames.short_description = 'Users'
