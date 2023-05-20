from django.urls import path

from budgets.views import budget_overview #, set_category_budget

app_name = 'budgets'

urlpatterns = [
    path('', budget_overview, name='budget_overview'),
    #path('set-category-budget/', set_category_budget, name='set_category_budget'),
]