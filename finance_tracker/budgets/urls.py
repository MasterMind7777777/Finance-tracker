from django.urls import path

from budgets.views import budget_overview, delete_budget

app_name = 'budgets'

urlpatterns = [
    path('', budget_overview, name='budget_overview'),
    path('delete-budget/<int:budget_id>/', delete_budget, name='delete_budget'),
]
