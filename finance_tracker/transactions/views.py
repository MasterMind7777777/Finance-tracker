from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from .models import Transaction
from .models import Category
from .forms import CategoryForm, TransactionForm
from django.db.models import Q
from datetime import datetime
from django.http import JsonResponse
from transactions.utils import CategoryEncoder
from django.core import serializers
import logging

# Set up a specific logger with our desired output level
logger = logging.getLogger(__name__)


@login_required
def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                logger.info(
                    "Transaction added successfully by user: %s",
                    request.user.username,
                )
                return redirect("users:dashboard")
            except Exception as e:
                error_message = str(e)
                logger.error(
                    "Error adding transaction by user %s: %s",
                    request.user.username,
                    error_message,
                )
        else:
            error_message = "Invalid form submission."
            logger.warning(
                "Invalid transaction form submission by user: %s",
                request.user.username,
            )
    else:
        form = TransactionForm()
        error_message = None

    return render(
        request,
        "transactions/add_transaction.html",
        {"form": form, "error_message": error_message},
    )


@login_required
@require_POST
def delete_transaction(request, transaction_id):
    try:
        # Get the transaction object
        transaction = get_object_or_404(Transaction, id=transaction_id)

        # Check if the transaction belongs to the current user
        if transaction.user != request.user:
            logger.warning(
                "User %s tried to delete transaction not owned by them: %s",
                request.user.username,
                transaction_id,
            )
            return HttpResponseForbidden(
                "You don't have permission to delete this transaction."
            )

        # Perform the delete operation
        transaction.delete()
        logger.info(
            "Transaction deleted successfully by user: %s",
            request.user.username,
        )

        # Redirect to the dashboard or any other appropriate page
        return redirect("users:dashboard")
    except Exception as e:
        error_message = str(e)
        logger.error(
            "Error deleting transaction (ID: %s) by user %s: %s",
            transaction_id,
            request.user.username,
            error_message,
        )
        return render(request, "error.html", {"error_message": error_message})


@login_required
def categories_view(request):
    try:
        categories = Category.objects.all()
        categories_data = serializers.serialize("json", categories)

        response_data = {
            "categories": categories_data,
        }

        return JsonResponse(response_data, safe=False)
    except Exception as e:
        error_message = str(e)
        logger.error(
            "Error retrieving categories by user %s: %s",
            request.user.username,
            error_message,
        )
        return render(request, "error.html", {"error_message": error_message})


@login_required
def manage_categories(request):
    try:
        categories = Category.objects.filter(user=request.user)
        form = CategoryForm()

        if request.method == "POST":
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save(commit=False)
                category.user = request.user
                category.save()
                logger.info(
                    "Category added successfully by user: %s",
                    request.user.username,
                )
                return redirect("transactions:manage_categories")
            else:
                logger.warning(
                    "Invalid category form submission by user: %s",
                    request.user.username,
                )

        context = {"categories": categories, "form": form}
        return render(request, "transactions/manage_categories.html", context)
    except Exception as e:
        error_message = str(e)
        logger.error(
            "Error managing categories by user %s: %s",
            request.user.username,
            error_message,
        )
        return render(request, "error.html", {"error_message": error_message})


@login_required
@require_POST
def delete_category(request, category_id):
    try:
        category = get_object_or_404(
            Category, pk=category_id, user=request.user
        )
        category.delete()
        logger.info(
            "Category (ID: %s) deleted successfully by user: %s",
            category_id,
            request.user.username,
        )
        return redirect("transactions:manage_categories")
    except Exception as e:
        error_message = str(e)
        logger.error(
            "Error deleting category (ID: %s) by user %s: %s",
            category_id,
            request.user.username,
            error_message,
        )
        return render(request, "error.html", {"error_message": error_message})


@login_required
def transaction_list(request):
    try:
        # Fetch all transactions for the current user
        user = request.user
        transactions = Transaction.objects.filter(
            user=user, parent_transaction=None
        )

        # Get the sort_by, filter_by, sort_order, and filter_value from the request's GET parameters
        sort_by = request.GET.get(
            "sort_field", "date"
        )  # Default to sorting by date
        filter_by = request.GET.get("filter_by", "")
        sort_order = request.GET.get(
            "sort_order", "asc"
        )  # Default to ascending order
        filter_value = request.GET.get("filter_value", "")

        lookup_mapping = {
            "category": "category__name__icontains",
            "title": "title__icontains",
            "description": "description__icontains",
            "amount": "amount",
            "date": "date",
            "field_name": "field_name__icontains",
        }

        if filter_by and filter_value:
            lookup_field = lookup_mapping.get(filter_by)
            if lookup_field:
                if filter_by == "date":
                    filter_value = datetime.strptime(
                        filter_value, "%Y-%m-%d"
                    ).date()
                transactions = transactions.filter(
                    **{lookup_field: filter_value}
                )
                logger.info(
                    f"Applied filter {filter_by} with value {filter_value} for user {user.username}"
                )

        categories = transactions.values_list(
            "category__name", flat=True
        ).distinct()

        if sort_by:
            if sort_order == "asc":
                transactions = transactions.order_by(sort_by)
            else:
                transactions = transactions.order_by(f"-{sort_by}")
            logger.info(
                f"Sorted transactions by {sort_by} in {sort_order} order for user {user.username}"
            )

        if request.method == "POST":
            form = TransactionForm(request.POST)
            if form.is_valid():
                try:
                    transaction = form.save(commit=False)
                    transaction.user = request.user
                    transaction.save()
                    logger.info(
                        f"Transaction added successfully by user {user.username}"
                    )
                    return redirect("transactions:transaction_list")
                except Exception as e:
                    error_message = str(e)
                    logger.error(
                        f"Error while saving transaction by user {user.username}: {error_message}"
                    )
            else:
                error_message = "Invalid form submission."
                logger.warning(
                    f"Invalid transaction form submission by user {user.username}"
                )
        else:
            form = TransactionForm()

        context = {
            "transactions": transactions,
            "categories": categories,
            "form": form,
        }
        return render(request, "transactions/transaction_list.html", context)

    except Exception as e:
        error_message = str(e)
        logger.error(
            f"General error in transaction_list view for user {request.user.username}: {error_message}"
        )
        return render(request, "error.html", {"error_message": error_message})


@login_required
def transaction_detail(request, pk):
    try:
        transaction = get_object_or_404(Transaction, pk=pk)
        logger.info(
            f"Retrieved transaction with ID {pk} for user {request.user.username}"
        )

        transactions = Transaction.objects.filter(parent_transaction_id=pk)

        if request.method == "POST":
            subtransaction_form = TransactionForm(request.POST)
            if subtransaction_form.is_valid():
                try:
                    subtransaction = subtransaction_form.save(commit=False)
                    subtransaction.user = request.user
                    subtransaction.parent_transaction = transaction

                    allowed_categories = Category.objects.filter(
                        Q(user=request.user)
                        & (
                            Q(pk=transaction.category.pk)
                            | Q(parent_category=transaction.category)
                        )
                    )
                    subtransaction_form.fields[
                        "category"
                    ].queryset = allowed_categories

                    subtransaction.save()
                    logger.info(
                        f"Subtransaction created for main transaction with ID {pk} by user {request.user.username}"
                    )

                    response_data = {
                        "id": subtransaction.id,
                        "title": subtransaction.title,
                        "description": subtransaction.description,
                        "amount": subtransaction.amount,
                        "category": subtransaction.category,
                        "date": subtransaction.date.strftime("%Y-%m-%d %H:%M"),
                    }
                    return JsonResponse(response_data, encoder=CategoryEncoder)
                except Exception as e:
                    error_message = str(e)
                    logger.error(
                        f"Error saving subtransaction for main transaction with ID {pk} by user {request.user.username}: {error_message}"
                    )
            else:
                error_message = "Invalid form submission."
                logger.warning(
                    f"Invalid subtransaction form submission for main transaction with ID {pk} by user {request.user.username}"
                )
        else:
            subtransaction_form = TransactionForm(
                initial={"category": transaction.category_id}
            )

            allowed_categories = Category.objects.filter(
                Q(user=request.user)
                & (
                    Q(pk=transaction.category.pk)
                    | Q(parent_category=transaction.category)
                )
            )
            subtransaction_form.fields[
                "category"
            ].queryset = allowed_categories

        context = {
            "transaction": transaction,
            "transactions": transactions,
            "subtransaction_form": subtransaction_form,
        }
        return render(request, "transactions/transaction_detail.html", context)
    except Exception as e:
        error_message = str(e)
        logger.error(
            f"General error in transaction_detail view for transaction ID {pk} and user {request.user.username}: {error_message}"
        )
        return render(request, "error.html", {"error_message": error_message})
