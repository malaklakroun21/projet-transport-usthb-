from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Register new user
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log in immediately after registration
            return redirect('home')  # Always redirect to homepage after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Login existing user
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('agent_dashboard')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


# Logout user
def logout_view(request):
    logout(request)
    return redirect('login')

# Profile page
@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})
