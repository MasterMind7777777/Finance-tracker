from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        # Perform login logic
        # Example:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard page
        else:
            # Invalid login credentials, show error message
            error_message = "Invalid username or password."
            return render(request, 'users/login.html', {'error_message': error_message})
    else:
        return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')
