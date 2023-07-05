from rest_framework import serializers
from budgets.models import CategoryBudget
from transactions.models import Category, Transaction

class CategoryBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryBudget
        fields = ['id', 'category', 'budget_limit']
        read_only_fields = ['id']

    def validate_category(self, value):
        # check if the category belongs to the current user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You do not have access to this category.")
        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'