from django.shortcuts import render, redirect

def home(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    else:
        return render(request, 'core/home.html')
