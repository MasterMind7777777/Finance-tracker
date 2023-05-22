from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoryBudgetForm
from .models import CategoryBudget
from transactions.models import Transaction, Category
from django.db.models import Sum

def budget_overview(request):
    # Retrieve all transactions for the current user
    transactions = Transaction.objects.filter(user=request.user)

    # Calculate the total income and expenses
    total_income = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum']
    total_expenses = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum']

    # Handle cases where the sums are None (no transactions or no amounts)
    total_income = total_income or 0
    total_expenses = total_expenses or 0

    # Calculate the current balance
    current_balance = total_income - total_expenses

    # Retrieve categories belonging to the user
    categories = Category.objects.filter(user=request.user)

    # Get currency
    user_currency = "$"

    # Get the budget limits and expenses for each category
    category_budgets = {}
    for category in categories:
        category_expenses = transactions.filter(category=category).aggregate(Sum('amount'))['amount__sum']
        try:
            category_budget = CategoryBudget.objects.get(category=category, user=request.user)
            remaining_budget = category_budget.budget_limit - category_expenses
        except CategoryBudget.DoesNotExist:
            category_budget = None
            remaining_budget = None
        category_budgets[category.name] = {
            'id': category_budget.id if category_budget else None,
            'budget_limit': category_budget.budget_limit if category_budget else None,
            'remaining_budget': remaining_budget,
            'amount_spent': category_expenses or 0,
            'currency': user_currency
        }

    if request.method == 'POST':
        form = CategoryBudgetForm(request.user, request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            budget_limit = form.cleaned_data['budget_limit']
            CategoryBudget.objects.update_or_create(category=category, user=request.user, defaults={'budget_limit': budget_limit})
            return redirect('budgets:budget_overview')
    else:
        form = CategoryBudgetForm(request.user)

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'category_budgets': category_budgets,
        'form': form,
        'user_currency': user_currency
    }

    return render(request, 'budgets/overview.html', context)

def delete_budget(request, budget_id):
    budget = get_object_or_404(CategoryBudget, id=budget_id)
    budget.delete()
    return redirect('budgets:budget_overview')