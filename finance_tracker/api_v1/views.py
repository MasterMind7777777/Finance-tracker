from decimal import Decimal
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, exceptions, parsers
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from budgets.models import CategoryBudget, CustomBudgetAlert
from analytics.utils import check_financial_health
from transactions.utils import forecast_expenses
from transactions.models import TransactionSplit
from transactions.models import Category, Transaction, RecurringTransaction
from .serializers import (
    TransactionSplitSerializer,
    UserSerializer,
    UserProfileSerializer,
    SocialMediaAccountSerializer,
    FriendRequestSerializer,
    CategoryBudgetSerializer,
    CategorySerializer,
    TransactionSerializer,
    SavingGoalSerializer,
)
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
from django.core.cache import cache
from budgets.tasks import generate_budget_alerts, check_budget_alerts
from transactions.tasks import prepare_transactions_chunks
from celery import current_task
from celery.result import AsyncResult
from finance_tracker.celery import app
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
import logging

# Setting up the logger at the top of your views file
logger = logging.getLogger(__name__)

User = get_user_model()


class CategoryBudgetViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        budgets = CategoryBudget.objects.filter(user=request.user)
        logger.info(f"Fetched budgets for user {request.user.username}")

        serializer = CategoryBudgetSerializer(
            budgets, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            budget = CategoryBudget.objects.get(pk=pk, user=request.user)
        except CategoryBudget.DoesNotExist:
            logger.warning(
                f"Budget with ID {pk} not found for user {request.user.username}"
            )
            return Response(
                {"error": "Budget not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CategoryBudgetSerializer(
            budget, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = CategoryBudgetSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Budget created for user {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(
            f"Invalid data provided by user {request.user.username} for budget creation: {serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            budget = CategoryBudget.objects.get(pk=pk, user=request.user)
        except CategoryBudget.DoesNotExist:
            logger.warning(
                f"Budget with ID {pk} not found for user {request.user.username}"
            )
            return Response(
                {"error": "Budget not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CategoryBudgetSerializer(
            budget, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Budget with ID {pk} updated for user {request.user.username}"
            )
            return Response(serializer.data)
        logger.warning(
            f"Invalid data provided by user {request.user.username} for budget update: {serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def create_custom_alert(self, request, pk):
        try:
            budget = CategoryBudget.objects.get(pk=pk, user=request.user)
        except CategoryBudget.DoesNotExist:
            logger.warning(
                f"Budget with ID {pk} not found for user {request.user.username}"
            )
            return Response(
                {"error": "Budget not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        alert = CustomBudgetAlert(
            message=request.data["message"],
            budget=budget,
            threshold=request.data["threshold"],
        )
        alert.save()
        logger.info(
            f"Custom alert created for budget with ID {pk} by user {request.user.username}"
        )
        return Response(
            {"message": "Custom alert created."},
            status=status.HTTP_201_CREATED,
        )

    def alerts(self, request):
        cache_key = f"alerts_task_{request.user.id}"
        task_status = cache.get(cache_key)

        if task_status is None:
            task = generate_budget_alerts.delay(request.user.id)
            cache.set(cache_key, task.id, timeout=None)
            logger.info(
                f"Started new budget alerts task for user {request.user.username}"
            )
            response_data = {"status": "Pending"}
            return JsonResponse(response_data, status=202)
        else:
            subtasks = cache.get(f"alerts_result_{request.user.id}")
            budget_alerts = check_budget_alerts(request.user.id)

            if budget_alerts.get("status") == "Error":
                task = generate_budget_alerts.delay(request.user.id)
                cache.set(cache_key, task.id, timeout=None)
                logger.error(
                    f"Error detected in budget alerts for user {request.user.username}. Restarting task."
                )
                response_data = {"status": "Pending"}
                return JsonResponse(response_data, status=202)

            all_sub_tasks_ready = all(
                AsyncResult(task_id).ready() for task_id in subtasks
            )
            if all_sub_tasks_ready:
                response_data = {"status": "Complete", "result": budget_alerts}
                cache.delete(cache_key)
                logger.info(
                    f"All subtasks for budget alerts completed for user {request.user.username}"
                )
                return JsonResponse(response_data, status=200)
            else:
                response_data = {"status": "Pending"}
                return JsonResponse(response_data, status=202)


class CategoryViewSet(viewsets.ModelViewSet, CreateModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.id

        # Validation
        if not self.is_valid_category(request.data):
            logger.warning(
                f"Invalid category data provided by user {request.user.username} request data: {request.data}"
            )
            raise ValidationError("Invalid category data")

        response = super().create(request, *args, **kwargs)

        if 200 <= response.status_code < 300:
            logger.info(
                f"Successfully created category for user {request.user.username}"
            )
        else:
            logger.error(
                f"Failed to create category for user {request.user.username}. Status code: {response.status_code}"
            )

        return response

    def update(self, request, *args, **kwargs):
        request.data["user"] = request.user.id

        # Validation
        if not self.is_valid_category(request.data):
            logger.warning(
                f"Invalid category data provided by user {request.user.username} for update"
            )
            raise ValidationError("Invalid category data for update")

        response = super().update(request, *args, **kwargs)

        if 200 <= response.status_code < 300:
            logger.info(
                f"Successfully updated category for user {request.user.username}"
            )
        else:
            logger.error(
                f"Failed to update category for user {request.user.username}. Status code: {response.status_code}"
            )

        return response

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(
                f"Attempting to delete category {instance.id} for user {request.user.username}"
            )
            self.perform_destroy(instance)
            logger.info(
                f"Successfully deleted category {instance.id} for user {request.user.username}"
            )
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValidationError as e:
            logger.warning(
                f"ValidationError while deleting category for user {request.user.username}: {str(e)}"
            )
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(
                f"Error while deleting category for user {request.user.username}: {str(e)}"
            )
            return Response(
                {"error": "An error occurred processing the request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def compare_spending(self, request, pk=None):
        user_id = request.user.id

        # Get friends_ids from the request data. Expect it to be a list.
        friends_ids = request.data.get("friends_ids")
        # Get period_days from the request data, with a default of 30
        period_days = int(request.data.get("period_days", 30))

        logger.info(
            f"Comparing spending for user {request.user.username} with friends: {friends_ids} over {period_days} days"
        )

        try:
            result = compare_spending(user_id, friends_ids, pk, period_days)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            logger.warning(
                f"ValueError in compare_spending for user {request.user.username}: {str(e)}"
            )
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            logger.warning(
                f"ValidationError in compare_spending for user {request.user.username}: {str(e)}"
            )
            return Response(
                {"error": str(e)}, status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(
                f"Error in compare_spending for user {request.user.username}: {str(e)}"
            )
            return Response(
                {"error": "An error occurred processing the request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def is_valid_category(self, data):
        # Implement your validation logic here.
        # For example, check if the category name or type is not empty.
        # Return True if the data is valid, otherwise return False.
        if not data.get("name") or not data.get("type"):
            return False
        return True


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter

    def create(self, request, *args, **kwargs):
        # Log the creation attempt
        logger.info(
            f"Attempt to create transaction for user {request.user.username}"
        )

        data = request.data.copy()
        data["user"] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Check if the transaction is recurring
        is_recurring = data.get("is_recurring", False)
        recurring_transaction_data = data.get("recurring_transaction_meta")

        if is_recurring and recurring_transaction_data:
            logger.info(
                f"Transaction is recurring for user {request.user.username}"
            )
            recurring_transaction = RecurringTransaction.objects.create(
                user=request.user,
                frequency=recurring_transaction_data.get("frequency"),
                start_date=recurring_transaction_data.get("start_date"),
                end_date=recurring_transaction_data.get("end_date"),
            )

            serializer.save(recurring_transaction=recurring_transaction)
        else:
            serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=False, methods=["get"])
    def forecast_expenses(self, request):
        logger.info(f"Forecasting expenses for user {request.user.username}")
        forecast_data = forecast_expenses(request.user.pk)
        return Response(forecast_data)

    @action(detail=True, methods=["post"])
    def split_transaction(self, request, pk=None):
        logger.info(
            f"Attempting to split transaction {pk} for user {request.user.username}"
        )

        transaction = self.get_object()
        splits = request.data.get("splits")

        if not splits:
            logger.warning(f"No splits provided for transaction {pk}")
            return Response(
                {"message": "No splits provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for split in splits:
            user_id = split.get("user")
            amount = Decimal(split.get("amount"))

            if not user_id or not amount:
                logger.warning(f"Invalid split data for transaction {pk}")
                return Response(
                    {
                        "message": "Each split must contain a 'user' and an 'amount'."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.get(id=user_id)
            split_record = TransactionSplit.objects.create(
                requester=transaction.user,
                requestee=user,
                transaction=transaction,
                amount=amount,
            )

        serialized_data = TransactionSplitSerializer(
            transaction.transactionsplit_set, many=True
        ).data
        return Response(serialized_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def bulk_upload(self, request):
        logger.info("Initiating bulk upload process.")
        file = request.FILES.get("file")
        user_id = request.user.id
        cache_key = f"bulk_upload_status_{user_id}"
        task_id = cache.get(cache_key)
        if task_id:
            task_result = AsyncResult(task_id)
            if task_result.ready():
                cache.delete(cache_key)
                logger.info("Task completed. Returning results.")
                return JsonResponse(task_result.result)
        if file and user_id:
            file_content = file.read().decode("utf-8")
            file = InMemoryUploadedFile(
                ContentFile(file_content.encode("utf-8")),
                "file",
                file.name,
                file.content_type,
                len(file_content),
                file.charset,
            )
            prepare_transactions_chunks.delay(file_content, user_id)
            logger.info("Bulk upload job queued successfully.")
            return JsonResponse({"status": "Pending"}, status=202)
        logger.warning("No file provided for bulk upload.")
        return JsonResponse({"error": "No file provided."}, status=400)

    @action(detail=False, methods=["GET"])
    def recommendations(self, request):
        logger.info("Generating recommendations.")
        user = request.user
        num_recommendations = int(
            request.query_params.get("num_recommendations", 5)
        )

        category_counts = (
            self.queryset.filter(user=user)
            .exclude(category=None)
            .values("category")
            .annotate(count=Count("category"))
            .order_by("-count")
        )
        most_used_category = (
            category_counts.first().get("category")
            if category_counts
            else None
        )
        if most_used_category:
            recommendations = self.queryset.filter(
                user=user, category=most_used_category
            )[:num_recommendations]
        else:
            recommendations = self.queryset.none()
        serializer = self.get_serializer(recommendations, many=True)
        data = {
            "recommendations": serializer.data,
            "most_used_category": most_used_category,
        }
        return Response(data)

    def savings_opportunities(self, request, category_id):
        logger.info("Calculating savings opportunities.")

        def round_floats(val):
            if isinstance(val, float):
                if val == float("inf"):
                    return "Infinity"
                elif val == float("-inf"):
                    return "-Infinity"
                else:
                    return round(val, 4)
            return val

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
                title_transactions[title].extend(
                    [False]
                    * (len(transactions) - len(title_transactions[title]))
                )

        # Find the selected category and its spending
        selected_category_spending = category_spending.get(category.id, 0)

        # Calculate potential savings by reducing spending in the selected category
        potential_savings = (
            float(selected_category_spending) * 0.1
        )  # Assume a 10% reduction in spending

        # Convert title_transactions to DataFrame
        title_transactions_df = DataFrame.from_dict(
            title_transactions, orient="index"
        ).transpose()

        # Perform association rule mining to discover associations between transaction titles
        if not title_transactions_df.empty:
            frequent_itemsets = apriori(
                title_transactions_df, min_support=0.1, use_colnames=True
            )
            association_rules_df = association_rules(
                frequent_itemsets, metric="confidence", min_threshold=0.7
            )
            # Convert frozensets in 'antecedents' and 'consequents' to lists
            association_rules_df["antecedents"] = association_rules_df[
                "antecedents"
            ].apply(list)
            association_rules_df["consequents"] = association_rules_df[
                "consequents"
            ].apply(list)

            # Round all float values in the DataFrame to 4 decimal places
            association_rules_df = association_rules_df.applymap(round_floats)
        else:
            # Empty DataFrame, no association rules to generate
            frequent_itemsets = []
            association_rules_df = DataFrame()

        # Create a list of savings opportunities
        opportunities = [
            {
                "category": category.name,
                "selected_category_spending": selected_category_spending,
                "potential_savings": round(float(potential_savings), 4),
                "correlations": [],
                "association_rules": association_rules_df.to_dict(
                    orient="records"
                ),
            }
        ]

        return Response(opportunities)

    def assign_category(self, request, *args, **kwargs):
        transaction_id = kwargs.get("transaction_id")
        user_id = request.user.pk
        logger.info(
            f"Assigning category for transaction {transaction_id} for user {user_id}."
        )
        response = categorize_transaction(transaction_id, user_id)
        return Response(response)


class TransactionSplitViewSet(viewsets.ViewSet):
    queryset = TransactionSplit.objects.all()
    allowed_methods = ["put", "get"]

    def list(self, request):
        logger.info("Listing transaction splits for user %s", request.user.id)
        queryset = TransactionSplit.objects.filter(
            Q(requester=request.user) | Q(requestee=request.user)
        )
        serializer = TransactionSplitSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["put"])
    def accept(self, request, pk=None):
        logger.info(
            "User %s is attempting to accept a transaction split with ID %s",
            request.user.id,
            pk,
        )
        transaction_split = get_object_or_404(
            TransactionSplit, pk=pk, requestee=request.user
        )

        with transaction.atomic():
            original_transaction = transaction_split.transaction

            # Create a new transaction with the amount from the TransactionSplit
            new_transaction = Transaction.objects.create(
                user=request.user,
                title=f"Split Transaction from {original_transaction.title}",
                amount=transaction_split.amount,
                date=original_transaction.date,
                currency=original_transaction.currency,
            )
            logger.info(
                "Created new transaction with ID %s for user %s",
                new_transaction.id,
                request.user.id,
            )

            # Update the status of the TransactionSplit to 'accepted'
            transaction_split.status = "accepted"
            transaction_split.save()
            logger.info(
                "Updated transaction split status to 'accepted' for split ID %s",
                transaction_split.id,
            )

            # Reduce the amount of the original transaction
            original_transaction.amount -= transaction_split.amount
            original_transaction.save()
            logger.info(
                "Updated original transaction amount for transaction ID %s",
                original_transaction.id,
            )

        return Response(
            {"status": "Transaction split accepted"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["put"])
    def decline(self, request, pk=None):
        logger.info(
            "User %s is attempting to decline a transaction split with ID %s",
            request.user.id,
            pk,
        )
        transaction_split = get_object_or_404(
            TransactionSplit, pk=pk, requestee=request.user
        )
        transaction_split.status = "declined"
        transaction_split.save()
        logger.info(
            "Updated transaction split status to 'declined' for split ID %s",
            transaction_split.id,
        )
        return Response(
            {"status": "Transaction split declined"}, status=status.HTTP_200_OK
        )


class FinancialHealthView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logger.info("Fetching financial health for user %s", request.user.id)
        financial_health = check_financial_health(request.user.id)
        return Response(financial_health)

    def create(self, request, user_id):
        logger.info(
            "Attempting to create financial health record for user %s by %s",
            user_id,
            request.user.id,
        )
        if not request.user.is_staff:
            logger.warning(
                "User %s unauthorized to create financial health record",
                request.user.id,
            )
            return Response(
                {
                    "detail": "You do not have permission to perform this action."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id)
        serializer = FinancialHealthSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            logger.info(
                "Financial health record created successfully for user %s",
                user_id,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(
            "Errors in financial health record creation for user %s: %s",
            user_id,
            serializer.errors,
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id):
        logger.info(
            "Attempting to update financial health record for user %s by %s",
            user_id,
            request.user.id,
        )
        if not request.user.is_staff:
            logger.warning(
                "User %s unauthorized to update financial health record",
                request.user.id,
            )
            return Response(
                {
                    "detail": "You do not have permission to perform this action."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        financial_health = FinancialHealth.objects.filter(
            user_id=user_id
        ).first()
        if not financial_health:
            logger.warning(
                "Financial health record not found for user %s", user_id
            )
            return Response(
                {
                    "detail": "Financial health record not found for the specified user."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FinancialHealthSerializer(
            financial_health, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                "Financial health record updated successfully for user %s",
                user_id,
            )
            return Response(serializer.data)
        logger.error(
            "Errors in updating financial health record for user %s: %s",
            user_id,
            serializer.errors,
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavingGoalViewSet(viewsets.ModelViewSet):
    queryset = SavingGoal.objects.all()
    serializer_class = SavingGoalSerializer

    def get_queryset(self):
        logger.info("Fetching saving goals for user %s", self.request.user.id)
        return self.queryset.filter(users=self.request.user)

    def perform_create(self, serializer):
        logger.info("Creating a saving goal for user %s", self.request.user.id)
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        if self.request.user != self.get_object().creator:
            logger.warning(
                "User %s tried to modify a saving goal not created by them",
                self.request.user.id,
            )
            raise exceptions.PermissionDenied(
                "Only the creator can modify this saving goal."
            )
        logger.info(
            "Updating a saving goal (ID: %s) by user %s",
            self.get_object().id,
            self.request.user.id,
        )
        serializer.save()

    @action(detail=True, methods=["post"])
    def add_users(self, request, pk=None):
        goal = self.get_object()
        if goal.creator != self.request.user:
            logger.warning(
                "User %s tried to add users to a saving goal not created by them",
                self.request.user.id,
            )
            return Response(
                {"message": "Only the creator can add users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Add users to the goal
        users_to_add = User.objects.filter(id__in=request.data["users"])
        goal.users.add(*users_to_add)
        goal.save()
        logger.info(
            "User %s added users to saving goal (ID: %s)",
            self.request.user.id,
            pk,
        )
        return Response({"message": "Users added successfully."})

    @action(detail=True, methods=["post"])
    def remove_users(self, request, pk=None):
        goal = self.get_object()
        if goal.creator != self.request.user:
            logger.warning(
                "User %s tried to remove users from a saving goal not created by them",
                self.request.user.id,
            )
            return Response(
                {"message": "Only the creator can remove users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Remove users from the goal
        users_to_remove = User.objects.filter(id__in=request.data["users"])
        goal.users.remove(*users_to_remove)
        goal.save()
        logger.info(
            "User %s removed users from saving goal (ID: %s)",
            self.request.user.id,
            pk,
        )
        return Response({"message": "Users removed successfully."})

    @action(detail=True, methods=["post"])
    def add_categories(self, request, pk=None):
        goal = self.get_object()
        user = self.request.user

        # Validate categories
        categories_to_add = Category.objects.filter(
            id__in=request.data["categories"]
        )

        if not categories_to_add.exists():
            logger.error("Invalid category IDs provided by user %s", user.id)
            return Response(
                {"message": "Invalid category IDs."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not all(category.user == user for category in categories_to_add):
            logger.warning(
                "User %s tried to add categories that do not belong to them",
                user.id,
            )
            return Response(
                {"message": "Some categories do not belong to the user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Add categories to the goal
        goal.categories.add(*categories_to_add)
        goal.save()
        logger.info(
            "User %s added categories to saving goal (ID: %s)", user.id, pk
        )
        return Response({"message": "Categories added successfully."})

    @action(detail=True, methods=["post"])
    def remove_categories(self, request, pk=None):
        goal = self.get_object()
        user = self.request.user

        # Validate categories
        categories_to_remove = Category.objects.filter(
            id__in=request.data["categories"]
        )

        if not categories_to_remove.exists():
            logger.error(
                "Invalid category IDs or categories do not belong to the user were provided by user %s",
                user.id,
            )
            return Response(
                {
                    "message": "Invalid category IDs or categories do not belong to the user."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not all(category.user == user for category in categories_to_remove):
            logger.warning(
                "User %s tried to remove categories that do not belong to them",
                user.id,
            )
            return Response(
                {"message": "Some categories do not belong to the user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Remove categories from the goal
        goal.categories.remove(*categories_to_remove)
        goal.save()
        logger.info(
            "User %s removed categories from saving goal (ID: %s)", user.id, pk
        )
        return Response({"message": "Categories removed successfully."})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            logger.info("User %s logged in successfully", username)
            refresh = RefreshToken.for_user(user)
            serialised_user = self.serializer_class(user).data
            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "user": serialised_user,
                }
            )
        else:
            logger.warning("Failed login attempt for username: %s", username)
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=True, methods=["get"])
    def profile(self, request, pk=None):
        logger.info("Fetching profile for user ID %s", pk)
        user = self.get_object()
        profile = user.userprofile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[parsers.MultiPartParser, parsers.FormParser],
    )
    def upload_profile_pic(self, request, *args, **kwargs):
        if "file" not in request.data:
            logger.error(
                "Image file not included in request by user %s",
                request.user.username,
            )
            return Response(
                {"file": "No image file included in request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.userprofile.profile_picture = request.data["file"]
        user.userprofile.save()
        logger.info("Profile picture updated for user %s", user.username)
        return Response(
            {"message": "Profile picture uploaded successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get", "post"])
    def social_media_accounts(self, request, pk=None):
        user = self.get_object()

        if request.method == "POST":
            logger.info(
                "Attempting to create a new social media account for user ID %s",
                pk,
            )
            serializer = SocialMediaAccountSerializer(data=request.data)
            serializer.context["user"] = user
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            logger.error(
                "Error while creating social media account for user ID %s: %s",
                pk,
                serializer.errors,
            )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        logger.info("Fetching social media accounts for user ID %s", pk)
        accounts = user.socialmediaaccount.all()
        serializer = SocialMediaAccountSerializer(accounts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def send_friend_request(self, request, pk=None):
        to_user = self.get_object()
        from_user = request.user

        if FriendRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).exists():
            logger.warning(
                "User %s tried to send a duplicate friend request to user %s",
                from_user.username,
                to_user.username,
            )
            return Response(
                {"detail": "Friend request already sent."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "User %s sent a friend request to user %s",
            from_user.username,
            to_user.username,
        )
        friend_request = FriendRequest.objects.create(
            from_user=from_user, to_user=to_user
        )
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def friends(self, request, pk=None):
        logger.info("Fetching friends for user ID %s", pk)
        user = self.get_object()
        friends = [friend.user2 for friend in user.friends.all()]
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def sent_friend_requests(self, request, pk=None):
        logger.info("Fetching sent friend requests for user ID %s", pk)
        user = self.get_object()
        requests = user.sent_friend_requests.all()
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def received_friend_requests(self, request, pk=None):
        logger.info("Fetching received friend requests for user ID %s", pk)
        user = self.get_object()
        requests = user.received_friend_requests.all()
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        logger.info(
            "User %s accepted friend request from user ID %s",
            request.user.username,
            pk,
        )
        friend_request = FriendRequest.objects.get(
            to_user=request.user, from_user_id=pk
        )
        friend_request.accept()
        return Response(
            {"detail": "Friend request accepted."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        logger.info(
            "User %s declined friend request from user ID %s",
            request.user.username,
            pk,
        )
        friend_request = FriendRequest.objects.get(
            to_user=request.user, from_user_id=pk
        )
        friend_request.decline()
        return Response(
            {"detail": "Friend request declined."}, status=status.HTTP_200_OK
        )
