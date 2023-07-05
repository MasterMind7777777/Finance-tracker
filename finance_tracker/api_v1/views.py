from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from budgets.models import CategoryBudget
from transactions.models import Category, Transaction
from transactions.models import Transaction
from .serializers import CategoryBudgetSerializer, CategorySerializer, TransactionSerializer

class CategoryBudgetViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = CategoryBudgetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            budget = CategoryBudget.objects.get(pk=pk, user=request.user)
        except CategoryBudget.DoesNotExist:
            return Response({'error': 'Budget not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategoryBudgetSerializer(budget, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def alerts(self, request):
        budgets = CategoryBudget.objects.filter(user=request.user)
        over_limit_categories = []
        for budget in budgets:
            total_spent = Transaction.objects.filter(user=request.user, category=budget.category).aggregate(Sum('amount'))['amount__sum'] or 0
            if total_spent > budget.budget_limit:
                over_limit_categories.append(budget.category.name)
        return Response({'over_limit_categories': over_limit_categories})


class CategoryViewSet(viewsets.ModelViewSet, CreateModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)
