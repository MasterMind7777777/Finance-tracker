from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import (CategoryBudgetViewSet, CategoryViewSet, 
                    TransactionViewSet, FinancialHealthView, 
                    SavingGoalViewSet, UserViewSet,
                    TransactionSplitViewSet)
from .react_loging_views import react_logging_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'api_v1'

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'budgets', CategoryBudgetViewSet, basename='budget')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'saving_goals', SavingGoalViewSet, basename='savinggoal')



urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('budgets/alerts/', CategoryBudgetViewSet.as_view({'get': 'alerts'}), name='budget-alerts'),
    path('transactions/recommendations/', TransactionViewSet.as_view({'get': 'recommendations'}), name='transaction-recommendations'),
    path('transactions/savings_opportunities/<int:category_id>', TransactionViewSet.as_view({'get': 'savings_opportunities'}), name='transaction-savings_opportunities'),
    path('transactions/<int:transaction_id>/assign_category', TransactionViewSet.as_view({'post': 'assign_category'}), name='transaction-assign_category'),
    path('transaction_splits/<int:pk>/accept/', TransactionSplitViewSet.as_view({'put': 'accept'}), name='transaction_split-accept'),
    path('transaction_splits/<int:pk>/decline/', TransactionSplitViewSet.as_view({'put': 'decline'}), name='transaction_split-decline'),
    path('transaction_splits/', TransactionSplitViewSet.as_view({'get': 'list'}), name='transaction_split-list'),
    path('financial-health/', FinancialHealthView.as_view(), name='financial-health'),
    path('react_logging/', react_logging_view, name='react_logging_view'),
]

urlpatterns += router.urls
