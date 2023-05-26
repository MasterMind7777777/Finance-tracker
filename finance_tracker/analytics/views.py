from django.shortcuts import render
from django.db.models import Sum
from transactions.models import Transaction, Category
from budgets.models import CategoryBudget

def analytics_view(request):
    # Expense Analytics
    total_expenses = Transaction.objects.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum']
    monthly_expenses = Transaction.objects.filter(category__type='expense').values('date__year', 'date__month').annotate(total=Sum('amount'))
    category_expenses = Category.objects.filter(transaction__category__type='expense').annotate(total=Sum('transaction__amount'))

    # Income Analytics
    total_income = Transaction.objects.filter(category__type='income').aggregate(Sum('amount'))['amount__sum']
    monthly_income = Transaction.objects.filter(category__type='income').values('date__year', 'date__month').annotate(total=Sum('amount'))

    # Budget Analytics
    budget_utilization = CategoryBudget.objects.annotate(total_expenses=Sum('category__transaction__amount')).values('category__name', 'budget_limit', 'total_expenses')

    # Transaction Analysis
    transactions = Transaction.objects.all()

    context = {
        'total_expenses': total_expenses,
        'monthly_expenses': monthly_expenses,
        'category_expenses': category_expenses,
        'total_income': total_income,
        'monthly_income': monthly_income,
        'budget_utilization': budget_utilization,
        'transactions': transactions,
    }

    return render(request, 'analytics/analytics.html', context)
