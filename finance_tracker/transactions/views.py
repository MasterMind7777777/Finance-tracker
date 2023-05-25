from django.shortcuts import render, redirect, get_object_or_404
from .forms import TransactionForm
from django.views.decorators.http import require_POST
from .models import Transaction
from .models import Category
from .forms import CategoryForm, TransactionForm
from django.db.models import Q
from datetime import datetime
from django.http import JsonResponse
from transactions.utils import CategoryEncoder

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('users:dashboard')
    else:
        form = TransactionForm()
    
    return render(request, 'transactions/add_transaction.html', {'form': form})


@require_POST
def delete_transaction(request, transaction_id):
    # Get the transaction object
    transaction = get_object_or_404(Transaction, id=transaction_id)

    # Perform the delete operation
    transaction.delete()

    # Redirect to the dashboard or any other appropriate page
    return redirect('users:dashboard')


def categories_view(request):
    # Fetch all categories from the database
    categories = Category.objects.all()

    # Convert categories to a list of dictionaries
    categories_list = [
        {'id': category.id, 'name': category.name}
        for category in categories
    ]

    # Create a dictionary to hold the categories list
    response_data = {
        'categories': categories_list
    }

    # Return the response as JSON
    return JsonResponse(response_data)


def manage_categories(request):
    categories = Category.objects.filter(user=request.user)
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('transactions:manage_categories')

    context = {
        'categories': categories,
        'form': form
    }
    return render(request, 'transactions/manage_categories.html', context)

@require_POST
def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id, user=request.user)
    category.delete()
    return redirect('transactions:manage_categories')


def transaction_list(request):
    # Fetch all transactions for the current user
    transactions = Transaction.objects.filter(user=request.user)

    # Get the sort_by, filter_by, sort_order, and filter_value from the request's GET parameters
    sort_by = request.GET.get('sort_field', 'date')  # Default to sorting by date
    filter_by = request.GET.get('filter_by', '')
    sort_order = request.GET.get('sort_order', 'asc')  # Default to ascending order
    filter_value = request.GET.get('filter_value', '')

    # Apply filtering based on filter_by and filter_value
    if filter_by and filter_value:
        if filter_by == 'category':
            transactions = transactions.filter(category__name__icontains=filter_value)
        elif filter_by == 'title':
            transactions = transactions.filter(title__icontains=filter_value)
        elif filter_by == 'description':
            transactions = transactions.filter(description__icontains=filter_value)
        elif filter_by == 'amount':
            filter_value = float(filter_value)
            transactions = transactions.filter(amount=filter_value)
        elif filter_by == 'date':
            # Parse the filter value as a date string and convert it to a datetime object
            filter_date = datetime.strptime(filter_value, '%Y-%m-%d').date()
            transactions = transactions.filter(date=filter_date)
        # Add more filters for other fields as needed
        elif filter_by == 'field_name':
            transactions = transactions.filter(field_name__icontains=filter_value)

    # Retrieve distinct categories from the filtered transactions
    categories = transactions.values_list('category__name', flat=True).distinct()

    # Apply sorting based on sort_by and sort_order
    if sort_by:
        if sort_order == 'asc':
            transactions = transactions.order_by(sort_by)
        else:
            transactions = transactions.order_by(f'-{sort_by}')

    # Handle form submission for main transaction
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transactions:transaction_list')

    else:
        form = TransactionForm()

    context = {
        'transactions': transactions,
        'categories': categories,
        'form': form,  # Pass the main transaction form to the template context
    }
    return render(request, 'transactions/transaction_list.html', context)

def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    # Retrieve child transactions
    child_transactions = Transaction.objects.filter(parent_transaction=transaction)

    # Handle form submission for subtransaction
    if request.method == 'POST' and 'add-subtransaction-form' in request.POST:
        subtransaction_form = TransactionForm(request.POST)
        if subtransaction_form.is_valid():
            subtransaction = subtransaction_form.save(commit=False)
            subtransaction.user = request.user
            subtransaction.parent_transaction = transaction
            subtransaction.save()
            return redirect('transactions:transaction_list')
    else:
        subtransaction_form = TransactionForm()

    context = {
        'transaction': transaction,
        'child_transactions': child_transactions,
        'subtransaction_form': subtransaction_form
    }
    return render(request, 'transactions/transaction_detail.html', context)
