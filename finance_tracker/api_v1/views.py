from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics, exceptions
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from budgets.models import CategoryBudget
from transactions.models import Category, Transaction, RecurringTransaction
from .serializers import (
    UserSerializer, UserProfileSerializer,
    SocialMediaAccountSerializer, FriendRequestSerializer,
    CategoryBudgetSerializer, CategorySerializer, 
    TransactionSerializer, SavingGoalSerializer)
from django.db.models import Count
from rest_framework.decorators import action
from pandas import DataFrame
from scipy.stats import pearsonr
from mlxtend.frequent_patterns import apriori, association_rules
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from analytics.models import FinancialHealth
from .serializers import FinancialHealthSerializer
from django.contrib.auth import get_user_model
from users.models import PushNotification, FriendRequest
from .filters import TransactionFilter
from capital.models import SavingGoal
from django.core.exceptions import ValidationError
from transactions.utils import categorize_transaction, compare_spending

User = get_user_model()

class CategoryBudgetViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = CategoryBudgetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            budget = CategoryBudget.objects.get(pk=pk, user=request.user)
        except CategoryBudget.DoesNotExist:
            return Response({'error': 'Budget not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategoryBudgetSerializer(budget, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def alerts(self, request):
        budgets = CategoryBudget.objects.filter(user__in=[request.user])
        over_limit_categories = []
        for budget in budgets:
            total_spent = Transaction.objects.filter(user=request.user, category=budget.category).aggregate(Sum('amount'))['amount__sum'] or 0
            if total_spent > budget.budget_limit:
                over_limit_categories.append(budget.category.name)
                PushNotification.objects.create(user=request.user, content='You have exceeded your budget limit for ' + budget.category.name)
        return Response({'over_limit_categories': over_limit_categories})


class CategoryViewSet(viewsets.ModelViewSet, CreateModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def compare_spending(self, request, pk=None):
        user_id = request.user.id

        # Get friends_ids from the request data. Expect it to be a list.
        friends_ids = request.data.get('friends_ids')
        # Get period_days from the request data, with a default of 30
        period_days = int(request.data.get('period_days', 30))

        try:
            result = compare_spending(user_id, friends_ids, pk, period_days)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)
            return Response({'error': 'An error occurred processing the request'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Check if the transaction is recurring
        is_recurring = data.get('is_recurring', False)
        recurring_transaction_data = data.get('recurring_transaction_meta')

        if is_recurring and recurring_transaction_data:
            recurring_transaction = RecurringTransaction.objects.create(
                user=request.user,
                frequency=recurring_transaction_data.get('frequency'),
                start_date=recurring_transaction_data.get('start_date'),
                end_date=recurring_transaction_data.get('end_date')
            )
            
            serializer.save(recurring_transaction=recurring_transaction)
        else:
            serializer.save()

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
    
    def savings_opportunities(self, request, category_id):
        # Retrieve the category object based on the category ID
        category = get_object_or_404(Category, id=category_id)
        user = request.user

        # Prepare data for analysis
        category_spending = {}
        title_transactions = {}

        transactions = Transaction.objects.filter(category=category, user=user)

        for transaction in transactions:
            amount = transaction.amount

            # Calculate total spending for the category
            if category.id in category_spending:
                category_spending[category.id] += amount
            else:
                category_spending[category.id] = amount

            # Group transactions by title
            title = transaction.title
            if title in title_transactions:
                title_transactions[title].append(True)
            else:
                title_transactions[title] = [True]
        
        # Fill missing values with False
        transaction_titles = title_transactions.keys()
        for title in transaction_titles:
            if len(title_transactions[title]) < len(transactions):
                title_transactions[title].extend([False] * (len(transactions) - len(title_transactions[title])))

        # Find the selected category and its spending
        selected_category_spending = category_spending.get(category.id, 0)

        # Calculate potential savings by reducing spending in the selected category
        potential_savings = float(selected_category_spending) * 0.1  # Assume a 10% reduction in spending
        
        # Convert title_transactions to DataFrame
        title_transactions_df = DataFrame.from_dict(title_transactions, orient="index").transpose()

        # Perform association rule mining to discover associations between transaction titles
        if not title_transactions_df.empty:
            frequent_itemsets = apriori(title_transactions_df, min_support=0.1, use_colnames=True)
            association_rules_df = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
            # Convert frozensets in 'antecedents' and 'consequents' to lists
            association_rules_df['antecedents'] = association_rules_df['antecedents'].apply(list)
            association_rules_df['consequents'] = association_rules_df['consequents'].apply(list)
        else:
            # Empty DataFrame, no association rules to generate
            frequent_itemsets = []
            association_rules_df = DataFrame()

        # Create a list of savings opportunities
        opportunities = [{
            "category": category.name,
            "potential_savings": float(potential_savings),
            "correlations": [],
            "association_rules": association_rules_df.to_dict(orient="records")
        }]

        return JsonResponse(opportunities, safe=False)
    
    def assign_category(self, request, *args, **kwargs):
        transaction_id = kwargs.get('transaction_id')
        user_id = request.user.pk

        categorize_transaction(transaction_id, user_id)

        return Response({'message': 'Transaction category assigned successfully'})




class FinancialHealthView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        financial_health = FinancialHealth.objects.filter(user=request.user).first()
        serializer = FinancialHealthSerializer(financial_health)
        return Response(serializer.data)

    def create(self, request, user_id):
        if not request.user.is_staff:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        user = User.objects.get(id=user_id)
        serializer = FinancialHealthSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id):
        if not request.user.is_staff:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        financial_health = FinancialHealth.objects.filter(user_id=user_id).first()
        if not financial_health:
            return Response({'detail': 'Financial health record not found for the specified user.'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = FinancialHealthSerializer(financial_health, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavingGoalViewSet(viewsets.ModelViewSet):
    queryset = SavingGoal.objects.all()
    serializer_class = SavingGoalSerializer

    def get_queryset(self):
        return self.queryset.filter(users=self.request.user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        if self.request.user != self.get_object().creator:
            raise exceptions.PermissionDenied("Only the creator can modify this saving goal.")
        serializer.save()

    @action(detail=True, methods=['post'])
    def add_users(self, request, pk=None):
        goal = self.get_object()
        if goal.creator != self.request.user:
            return Response({"message": "Only the creator can add users."}, status=status.HTTP_403_FORBIDDEN)

        # Add users to the goal
        users_to_add = User.objects.filter(id__in=request.data['users'])
        goal.users.add(*users_to_add)
        goal.save()
        return Response({"message": "Users added successfully."})

    @action(detail=True, methods=['post'])
    def remove_users(self, request, pk=None):
        goal = self.get_object()
        if goal.creator != self.request.user:
            return Response({"message": "Only the creator can remove users."}, status=status.HTTP_403_FORBIDDEN)

        # Remove users from the goal
        users_to_remove = User.objects.filter(id__in=request.data['users'])
        goal.users.remove(*users_to_remove)
        goal.save()
        return Response({"message": "Users removed successfully."})

    @action(detail=True, methods=['post'])
    def add_categories(self, request, pk=None):
        goal = self.get_object()
        user = self.request.user

        # Validate categories
        categories_to_add = Category.objects.filter(id__in=request.data['categories'])

        if not categories_to_add.exists():
            return Response({"message": "Invalid category IDs."}, status=status.HTTP_404_NOT_FOUND)
        if not all(category.user == user for category in categories_to_add):
            return Response({"message": "Some categories do not belong to the user."}, status=status.HTTP_403_FORBIDDEN)
        
        # Add categories to the goal
        goal.categories.add(*categories_to_add)
        goal.save()
        print(goal)
        return Response({"message": "Categories added successfully."})

    @action(detail=True, methods=['post'])
    def remove_categories(self, request, pk=None):
        goal = self.get_object()
        user = self.request.user

        # Validate categories
        categories_to_remove = Category.objects.filter(id__in=request.data['categories'])

        if not categories_to_remove.exists():
            return Response({"message": "Invalid category IDs or categories do not belong to the user."}, status=status.HTTP_400_BAD_REQUEST)

        if not all(category.user == user for category in categories_to_remove):
            return Response({"message": "Some categories do not belong to the user."}, status=status.HTTP_403_FORBIDDEN)

        # Remove categories from the goal
        goal.categories.remove(*categories_to_remove)
        goal.save()
        return Response({"message": "Categories removed successfully."})
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        user = self.get_object()
        profile = user.userprofile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])  # Allow GET and POST requests
    def social_media_accounts(self, request, pk=None):
        user = self.get_object()

        if request.method == 'POST':
            # If it's a POST request, create a new social media account
            serializer = SocialMediaAccountSerializer(data=request.data)
            serializer.context['user'] = user  # Pass the user to the serializer context
            print(user)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If it's a GET request, retrieve existing social media accounts
        accounts = user.socialmediaaccount.all()
        serializer = SocialMediaAccountSerializer(accounts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def sent_friend_requests(self, request, pk=None):
        user = self.get_object()
        requests = user.sent_friend_requests.all()
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def received_friend_requests(self, request, pk=None):
        user = self.get_object()
        requests = user.received_friend_requests.all()
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friend_request = FriendRequest.objects.get(to_user=request.user, from_user_id=pk)
        friend_request.accept()
        return Response({'detail': 'Friend request accepted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        friend_request = FriendRequest.objects.get(to_user=request.user, from_user_id=pk)
        friend_request.decline()
        return Response({'detail': 'Friend request declined.'}, status=status.HTTP_200_OK)