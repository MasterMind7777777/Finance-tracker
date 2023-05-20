from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('add/', views.add_transaction, name='add_transaction'),
    path('<int:transaction_id>/delete/', views.delete_transaction, name='delete_transaction'),
    path('manage-categories/', views.manage_categories, name='manage_categories'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('', views.transaction_list, name='transaction_list'),
    path('<int:pk>/', views.transaction_detail, name='transaction_detail'),
]
