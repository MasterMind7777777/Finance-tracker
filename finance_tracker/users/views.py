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
            error_message = "Invalid form submission."
    else:
        form = CustomUserCreationForm()

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
            error_message = "Invalid form submission."
    else:
        form = CustomAuthenticationForm()

    return render(request, 'users/login.html', {'form': form, 'error_message': error_message})

def user_logout(request):
    logout(request)
    return redirect('users:login')


@login_required
def dashboard(request):
    user = request.user
    transactions = user.transaction_set.filter(parent_transaction=None)
    error_message = ""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                form.instance.user = user
                transaction = form.save()

                # Return the newly created transaction as JSON response
                response_data = {
                    'id': transaction.id,
                    'title': transaction.title,
                    'description': transaction.description,
                    'amount': transaction.amount,
                    'category': transaction.category,
                    'date': transaction.date.strftime('%Y-%m-%d %H:%M')  # Format the date as needed
                }
                return JsonResponse(response_data, encoder=CategoryEncoder)
            except Exception as e:
                error_message = str(e)
        else:
            error_message = "Invalid form submission."
    else:
        form = TransactionForm()

    context = {
        'transactions': transactions,
        'form': form,
        'error_message': error_message
    }

    return render(request, 'users/dashboard.html', context)
