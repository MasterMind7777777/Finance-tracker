from decimal import Decimal
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, exceptions, parsers
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from budgets.models import CategoryBudget, CustomBudgetAlert
from analytics.utils import check_financial_health
from transactions.utils import forecast_expenses
from transactions.models import TransactionSplit
from transactions.models import Category, Transaction, RecurringTransaction
from .serializers import (
    TransactionSplitSerializer, UserSerializer, UserProfileSerializer,
    SocialMediaAccountSerializer, FriendRequestSerializer,
    CategoryBudgetSerializer, CategorySerializer, 
    TransactionSerializer, SavingGoalSerializer)
from django.db.models import Count
from rest_framework.decorators import action
from pandas import DataFrame
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
import csv
from django.core.cache import cache
from budgets.tasks import generate_budget_alerts, check_budget_alerts
from transactions.tasks import prepare_transactions_chunks
from celery import current_task
from celery.result import AsyncResult
from finance_tracker.celery import app
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

User = get_user_model()

class CategoryBudgetViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        budgets = CategoryBudget.objects.filter(user=request.user)
        serializer = CategoryBudgetSerializer(budgets, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            budget = CategoryBudget.objects.get(pk=pk, user=request.user)
        except CategoryBudget.DoesNotExist:
            return Response({'error': 'Budget not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategoryBudgetSerializer(budget, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    @action(detail=True, methods=['post'])
    def create_custom_alert(self, request, pk):
        try:
            budget = CategoryBudget.objects.get(pk=pk, user=request.user)
        except CategoryBudget.DoesNotExist:
            return Response({'error': 'Budget not found.'}, status=status.HTTP_404_NOT_FOUND)

        alert = CustomBudgetAlert(
            message=request.data['message'],
            budget=budget,
            threshold=request.data['threshold']
        )
        alert.save()
        return Response({'message': 'Custom alert created.'}, status=status.HTTP_201_CREATED)

    def alerts(self, request):
        cache_key = f"alerts_task_{request.user.id}"
        task_status = cache.get(cache_key)

        if task_status is None:
            task = generate_budget_alerts.delay(request.user.id)
            cache.set(cache_key, task.id, timeout=None)
            response_data = {
                'status': 'Pending'
            }
            return JsonResponse(response_data, status=202)  # Status code 202 for Pending
        else:
            subtasks = cache.get(f"alerts_result_{request.user.id}")
            budget_alerts = check_budget_alerts(request.user.id)
            
            if budget_alerts.get('status') == 'Error':
                task = generate_budget_alerts.delay(request.user.id)
                cache.set(cache_key, task.id, timeout=None)
                response_data = {
                'status': 'Pending'
                }
                return JsonResponse(response_data, status=202)  # Status code 202 for Pending
            
            all_sub_tasks_ready = all(AsyncResult(task_id).ready() for task_id in subtasks)
            if all_sub_tasks_ready:
                response_data = {
                    'status': 'Complete',
                    'result': budget_alerts
                }
                cache.delete(cache_key)  # Remove completed task from cache
                return JsonResponse(response_data, status=200)  # Status code 200 for Complete
            else:
                response_data = {
                    'status': 'Pending'
                }
                return JsonResponse(response_data, status=202)  # Status code 202 for Pending


class CategoryViewSet(viewsets.ModelViewSet, CreateModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().update(request, *args, **kwargs)
    
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
    
    @action(detail=False, methods=['get'])
    def forecast_expenses(self, request):
        forecast_data = forecast_expenses(request.user.pk)
        return Response(forecast_data)

    @action(detail=True, methods=['post'])
    def split_transaction(self, request, pk=None):
        transaction = self.get_object()
        splits = request.data.get('splits')

        if not splits:
            return Response({"message": "No splits provided."}, status=status.HTTP_400_BAD_REQUEST)

        for split in splits:
            user_id = split.get('user')
            amount = Decimal(split.get('amount'))

            if not user_id or not amount:
                return Response({"message": "Each split must contain a 'user' and an 'amount'."}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=user_id)
            split_record = TransactionSplit.objects.create(requester=transaction.user, requestee=user, transaction=transaction, amount=amount)

        serialized_data = TransactionSplitSerializer(transaction.transactionsplit_set, many=True).data
        return Response(serialized_data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['POST'])
    def bulk_upload(self, request):
        file = request.FILES.get('file')
        user_id = request.user.id
        if file and user_id:
            # Convert file content to string
            file_content = file.read().decode('utf-8')

            # Reconstruct the file because file.read() was already called
            file = InMemoryUploadedFile(
                ContentFile(file_content.encode('utf-8')),
                'file',
                file.name,
                file.content_type,
                len(file_content),
                file.charset
            )

            prepare_transactions_chunks.delay(file_content, user_id)
            return JsonResponse({'status': 'Pending'}, status=202)
        return JsonResponse({'error': 'No file provided.'}, status=400)
    
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


class TransactionSplitViewSet(viewsets.ViewSet):
    queryset = TransactionSplit.objects.all()
    allowed_methods = ['put']

    @action(detail=True, methods=['put'])
    def accept(self, request, pk=None):
        transaction_split = get_object_or_404(TransactionSplit, pk=pk, requestee=request.user)

        with transaction.atomic():
            original_transaction = transaction_split.transaction

            # Create a new transaction with the amount from the TransactionSplit
            new_transaction = Transaction.objects.create(
                user=request.user,
                title=f"Split Transaction from {original_transaction.title}",
                amount=transaction_split.amount,
                date=original_transaction.date,
                currency=original_transaction.currency
            )

            # Update the status of the TransactionSplit to 'accepted'
            transaction_split.status = 'accepted'
            transaction_split.save()

            # Reduce the amount of the original transaction
            original_transaction.amount -= transaction_split.amount
            original_transaction.save()

        return Response({'status': 'Transaction split accepted'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def decline(self, request, pk=None):
        transaction_split = get_object_or_404(TransactionSplit, pk=pk, requestee=request.user)
        transaction_split.status = 'declined'
        transaction_split.save()
        return Response({'status': 'Transaction split declined'}, status=status.HTTP_200_OK)


class FinancialHealthView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        financial_health = check_financial_health(request.user.id)
        return Response(financial_health)

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

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({'access_token': str(refresh.access_token)})
        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        user = self.get_object()
        profile = user.userprofile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], parser_classes=[parsers.MultiPartParser, parsers.FormParser])
    def upload_profile_pic(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({"file": "No image file included in request"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.userprofile.profile_picture = request.data['file']
        user.userprofile.save()
        
        return Response({"message": "Profile picture uploaded successfully"}, status=status.HTTP_200_OK)

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