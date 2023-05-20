from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from transactions.utils import CategoryEncoder
from transactions.forms import TransactionForm
from transactions.models import Transaction
from django.http import JsonResponse


def signup(request):
    error_message = ""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
        error_message = None

    return render(request, 'users/signup.html', {'form': form, 'error_message': error_message})

def user_login(request):
    error_message = ""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('users:dashboard')  # Redirect to the dashboard page
        else:
            error_message = "Invalid username or password."
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form, 'error_message': error_message})

def user_logout(request):
    logout(request)
    return redirect('users:login')


@login_required
def dashboard(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    form = TransactionForm()

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = user
            transaction.save()

            # Return the newly created transaction as JSON response
            return JsonResponse({
                'id': transaction.id,
                'title': transaction.title,
                'description': transaction.description,
                'amount': transaction.amount,
                'category': transaction.category,
                'date': transaction.date.strftime('%Y-%m-%d %H:%M')  # Format the date as needed
            }, encoder=CategoryEncoder)

    context = {
        'transactions': transactions,
        'form': form
    }

    return render(request, 'users/dashboard.html', context)