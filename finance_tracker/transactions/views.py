from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Transaction
from .models import Category
from .forms import CategoryForm, TransactionForm
from django.db.models import Q
from datetime import datetime
from django.http import JsonResponse
from transactions.utils import CategoryEncoder
from django.core import serializers


def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                return redirect('users:dashboard')
            except Exception as e:
                error_message = str(e)
        else:
            error_message = "Invalid form submission."
    else:
        form = TransactionForm()
        error_message = None
    
    return render(request, 'transactions/add_transaction.html', {'form': form, 'error_message': error_message})


@require_POST
def delete_transaction(request, transaction_id):
    try:
        # Get the transaction object
        transaction = get_object_or_404(Transaction, id=transaction_id)

        # Perform the delete operation
        transaction.delete()

        # Redirect to the dashboard or any other appropriate page
        return redirect('users:dashboard')
    except Exception as e:
        error_message = str(e)
        return render(request, 'error.html', {'error_message': error_message})


def categories_view(request):
    try:
        categories = Category.objects.all()
        categories_data = serializers.serialize('json', categories)
        
        response_data = {
            'categories': categories_data,
        }

        return JsonResponse(response_data, safe=False)
    except Exception as e:
        error_message = str(e)
        return render(request, 'error.html', {'error_message': error_message})


def manage_categories(request):
    try:
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
    except Exception as e:
        error_message = str(e)
        return render(request, 'error.html', {'error_message': error_message})

@require_POST
def delete_category(request, category_id):
    try:
        category = get_object_or_404(Category, pk=category_id, user=request.user)
        category.delete()
        return redirect('transactions:manage_categories')
    except Exception as e:
        error_message = str(e)
        return render(request, 'error.html', {'error_message': error_message})


def transaction_list(request):
    try:
        # Fetch all transactions for the current user
        user = request.user
        transactions = Transaction.objects.filter(user=user, parent_transaction=None)

        # Get the sort_by, filter_by, sort_order, and filter_value from the request's GET parameters
        sort_by = request.GET.get('sort_field', 'date')  # Default to sorting by date
        filter_by = request.GET.get('filter_by', '')
        sort_order = request.GET.get('sort_order', 'asc')  # Default to ascending order
        filter_value = request.GET.get('filter_value', '')

        # Mapping of filter fields to lookup fields
        lookup_mapping = {
            'category': 'category__name__icontains',
            'title': 'title__icontains',
            'description': 'description__icontains',
            'amount': 'amount',
            'date': 'date',
            'field_name': 'field_name__icontains'
            # Add more fields as needed
        }

        # Apply filtering based on filter_by and filter_value
        if filter_by and filter_value:
            lookup_field = lookup_mapping.get(filter_by)
            if lookup_field:
                if filter_by == 'date':
                    filter_value = datetime.strptime(filter_value, '%Y-%m-%d').date()
                transactions = transactions.filter(**{lookup_field: filter_value})

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
                try:
                    transaction = form.save(commit=False)
                    transaction.user = request.user
                    transaction.save()
                    return redirect('transactions:transaction_list')
                except Exception as e:
                    error_message = str(e)
            else:
                error_message = "Invalid form submission."
        else:
            form = TransactionForm()

        context = {
            'transactions': transactions,
            'categories': categories,
            'form': form,  # Pass the main transaction form to the template context
        }
        return render(request, 'transactions/transaction_list.html', context)
    except Exception as e:
        error_message = str(e)
        return render(request, 'error.html', {'error_message': error_message})

def transaction_detail(request, pk):
    try:
        transaction = get_object_or_404(Transaction, pk=pk)

        # Retrieve child transactions
        transactions = Transaction.objects.filter(parent_transaction_id=pk)

        # Handle form submission for subtransaction
        if request.method == 'POST':
            subtransaction_form = TransactionForm(request.POST)
            if subtransaction_form.is_valid():
                try:
                    subtransaction = subtransaction_form.save(commit=False)
                    subtransaction.user = request.user
                    subtransaction.parent_transaction = transaction

                    # Retrieve allowed categories including parent category and its subcategories
                    allowed_categories = Category.objects.filter(Q(user=request.user) & (Q(pk=transaction.category.pk) | Q(parent_category=transaction.category)))
                    subtransaction_form.fields['category'].queryset = allowed_categories

                    subtransaction.save()
                    # Return the newly created transaction as JSON response
                    response_data = {
                        'id': subtransaction.id,
                        'title': subtransaction.title,
                        'description': subtransaction.description,
                        'amount': subtransaction.amount,
                        'category': subtransaction.category,
                        'date': subtransaction.date.strftime('%Y-%m-%d %H:%M')  # Format the date as needed
                    }
                    return JsonResponse(response_data, encoder=CategoryEncoder)
                except Exception as e:
                    error_message = str(e)
            else:
                error_message = "Invalid form submission."
        else:
            subtransaction_form = TransactionForm(initial={'category': transaction.category_id})

            # Retrieve allowed categories including parent category and its subcategories
            allowed_categories = Category.objects.filter(Q(user=request.user) & (Q(pk=transaction.category.pk) | Q(parent_category=transaction.category)))
            subtransaction_form.fields['category'].queryset = allowed_categories

        context = {
            'transaction': transaction,
            'transactions': transactions,
            'subtransaction_form': subtransaction_form,
        }
        return render(request, 'transactions/transaction_detail.html', context)
    except Exception as e:
        error_message = str(e)
        return render(request, 'error.html', {'error_message': error_message})
