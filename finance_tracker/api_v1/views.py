from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from budgets.models import CategoryBudget
from transactions.models import Category, Transaction
from transactions.models import Transaction
from .serializers import CategoryBudgetSerializer, CategorySerializer, TransactionSerializer
from django.db.models import Count
from rest_framework.decorators import action

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
        data = request.data.copy()  # create mutable copy
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    
    @action(detail=False, methods=['GET'])
    def recommendations(self, request):
        user = request.user
        num_recommendations = int(request.query_params.get('num_recommendations', 5))  # Default to 5 recommendations
        
        # Get category counts first
        category_counts = self.queryset.filter(user=user).exclude(category=None).values('category').annotate(count=Count('category')).order_by('-count')
        
        most_used_category = category_counts.first().get('category') if category_counts else None

        # Then get the recommendations based on the most used categories
        if most_used_category:
            recommendations = self.queryset.filter(user=user, category=most_used_category)[:num_recommendations]
        else:
            recommendations = self.queryset.none()  # Empty queryset

        serializer = self.get_serializer(recommendations, many=True)
        data = {
            'recommendations': serializer.data,
            'most_used_category': most_used_category,
        }
        return Response(data)
