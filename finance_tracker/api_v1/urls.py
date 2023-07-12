from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (CategoryBudgetViewSet, CategoryViewSet, 
                    TransactionViewSet, FinancialHealthView, 
                    SavingGoalViewSet, UserViewSet)

app_name = 'api_v1'

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'budgets', CategoryBudgetViewSet, basename='budget')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'saving_goals', SavingGoalViewSet, basename='savinggoal')


urlpatterns = [
    path('budgets/alerts/', CategoryBudgetViewSet.as_view({'get': 'alerts'}), name='budget-alerts'),
    path('transactions/recommendations/', TransactionViewSet.as_view({'get': 'recommendations'}), name='transaction-recommendations'),
    path('transactions/savings_opportunities/<int:category_id>', TransactionViewSet.as_view({'get': 'savings_opportunities'}), name='transaction-savings_opportunities'),
    path('transactions/<int:transaction_id>/assign_category', TransactionViewSet.as_view({'post': 'assign_category'}), name='transaction-assign_category'),
    path('financial-health/', FinancialHealthView.as_view(), name='financial-health'),
    # other paths...
]

urlpatterns += router.urls