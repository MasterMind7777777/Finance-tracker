from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import CategoryBudgetViewSet, CategoryViewSet, TransactionViewSet

app_name = 'api_v1'

router = SimpleRouter()
router.register(r'budgets', CategoryBudgetViewSet, basename='budget')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('budgets/alerts/', CategoryBudgetViewSet.as_view({'get': 'alerts'}), name='budget-alerts'),
    path('transactions/recommendations/', TransactionViewSet.as_view({'get': 'recommendations'}), name='transaction-recommendations'),
    # other paths...
]

urlpatterns += router.urls