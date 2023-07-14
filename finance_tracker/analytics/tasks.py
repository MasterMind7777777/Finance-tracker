from django.db.models import Sum
from django.shortcuts import get_object_or_404
from .models import FinancialHealth
from transactions.models import Category, Transaction
from django.db import transaction
from django.contrib.auth import get_user_model
from api_v1.serializers import FinancialHealthSerializer
from decimal import Decimal
from finance_tracker.celery import app

User = get_user_model()

@app.task
def create_financial_health_task(user_id):
    user = get_object_or_404(User, id=user_id)

    transactions = Transaction.objects.filter(user=user).prefetch_related('category')

    income_amount = transactions.filter(category__type=Category.INCOME).aggregate(amount=Sum('amount'))['amount'] or 0
    expense_amount = transactions.filter(category__type=Category.EXPENSE).aggregate(amount=Sum('amount'))['amount'] or 0
    saving_amount = transactions.filter(category__type=Category.SAVING).aggregate(amount=Sum('amount'))['amount'] or 0
    investment_amount = transactions.filter(category__type=Category.INVESTMENT).aggregate(amount=Sum('amount'))['amount'] or 0

    with transaction.atomic():
        financial_health = FinancialHealth.objects.create(
            user=user,
            income=income_amount,
            expenditure=expense_amount,
            savings=saving_amount,
            investments=investment_amount
        )

    financial_advice = []

    # Calculate ratios
    saving_ratio = saving_amount / income_amount if income_amount else 0
    expense_ratio = expense_amount / income_amount if income_amount else 0
    investment_ratio = investment_amount / income_amount if income_amount else 0

    financial_advice = {
        "low_savings": {"condition": lambda: saving_ratio < Decimal('0.2'), "message": "Your savings are less than 20% of your income. It's recommended to aim for at least 20%.", "score": 800},
        "high_expenses": {"condition": lambda: expense_ratio > Decimal('0.6'), "message": "Your expenses are more than 60% of your income. Consider reducing unnecessary expenses.", "score": 850},
        "low_investments": {"condition": lambda: investment_ratio < Decimal('0.1'), "message": "Your investments are less than 10% of your income. It could be beneficial to increase this to grow your wealth.", "score": 750},
        "insufficient_emergency_fund": {"condition": lambda: saving_amount < expense_amount * Decimal('3'), "message": "Your savings are less than three months of expenses. It's recommended to have an emergency fund covering at least 3-6 months of expenses.", "score": 1000},
        "investments_below_income": {"condition": lambda: investment_amount < income_amount * Decimal('0.1'), "message": "Your investments are less than 10% of your income. To grow your wealth and beat inflation, consider investing a larger proportion of your income.", "score": 700},
        "expenses_exceeding_income": {"condition": lambda: expense_amount > income_amount * Decimal('0.8'), "message": "Your expenses are over 80% of your income. It's recommended to reduce your expenses or increase your income to achieve a healthier financial balance.", "score": 950},
        "savings_below_expenses": {"condition": lambda: saving_amount < expense_amount * Decimal('0.2'), "message": "Your savings are less than 20% of your expenses. It's important to save more to secure your financial future.", "score": 900},
        "investments_exceeding_savings": {"condition": lambda: investment_amount > saving_amount, "message": "Your investments are higher than your savings. It's crucial to maintain a healthy balance as savings provide a safety net during financial emergencies.", "score": 650},
    }

    # Adjust financial advice based on income_amount
    if income_amount >= Decimal('50000'):
        financial_advice["low_savings"]["condition"] = lambda: saving_ratio < Decimal('0.25')
        financial_advice["low_investments"]["condition"] = lambda: investment_ratio < Decimal('0.12')
        financial_advice["insufficient_emergency_fund"]["message"] = "Your savings are less than four to six months of expenses. It's recommended to have an emergency fund covering at least 4-6 months of expenses."

    if income_amount >= Decimal('100000'):
        financial_advice["low_savings"]["condition"] = lambda: saving_ratio < Decimal('0.30')
        financial_advice["low_investments"]["condition"] = lambda: investment_ratio < Decimal('0.15')
        financial_advice["insufficient_emergency_fund"]["message"] = "Your savings are less than six to nine months of expenses. It's recommended to have an emergency fund covering at least 6-9 months of expenses."

    if income_amount >= Decimal('200000'):
        financial_advice["low_savings"]["condition"] = lambda: saving_ratio < Decimal('0.35')
        financial_advice["low_investments"]["condition"] = lambda: investment_ratio < Decimal('0.18')
        financial_advice["insufficient_emergency_fund"]["message"] = "Your savings are less than nine to twelve months of expenses. It's recommended to have an emergency fund covering at least 9-12 months of expenses."


    total_score = sum(advice["score"] for advice in financial_advice.values())
    user_score = 0

    financial_advice_messages = []
    for advice in financial_advice.values():
        if advice["condition"]():
            financial_advice_messages.append(advice["message"])
            user_score += advice["score"]

    # Calculate financial health score based on ratios to income
    financial_health_score = user_score / total_score * 100

    # Upadate FinancialHealth object
    financial_health.advice = '\n'.join(financial_advice_messages)
    financial_health.score = financial_health_score
    financial_health.save()

    serializer = FinancialHealthSerializer(financial_health)
    return serializer.data
