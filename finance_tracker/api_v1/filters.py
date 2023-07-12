from django_filters import rest_framework as filters
from transactions.models import Transaction, Category

class TransactionFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name='user__id')
    category_id = filters.NumberFilter(field_name='category__id')
    date_from = filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['user_id', 'category_id', 'date_from', 'date_to']