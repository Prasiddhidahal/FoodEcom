from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model, logout  # Correct way to reference the user model

User = get_user_model()  # Correctly retrieve the user model

@csrf_protect
def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Save the new user object
            new_user = form.save()

            # Retrieve the username for success message
            usernames = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {usernames}!')

            # Authenticate the new user
            new_user = authenticate(username=form.cleaned_data['email'],  # Authenticate by email
                                    password=form.cleaned_data['password1'])

            # Log in the user and redirect
            if new_user is not None:
                login(request, new_user)
                return redirect('core:index')  # Redirect to home page after registration
    else:
        form = UserRegisterForm()

    # Pass form to template context
    context = {
        'form': form,
    }
    return render(request, 'userauth/register.html', context)


@csrf_protect
def user_login(request):
    # If the user is already authenticated, redirect them to the homepage
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in.")
        return redirect('core:index')

    # Handle POST request to login the user
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Try to retrieve the user based on the email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.warning(request, f'No user found with the email {email}. Please try again.')
            return render(request, "userauth/login.html")

        # Authenticate the user using username (email is mapped to username in this case)
        user = authenticate(request, username=user.username, password=password)

        # If authentication is successful, log the user in and redirect to the homepage
        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect("core:index")
        else:
            # If authentication fails, show an error message
            messages.warning(request, "Incorrect password. Please try again.")

    # Return the login page if it's not a POST request
    return render(request, "userauth/login.html")

def user_logout(request):
    # Check if the user is authenticated before logging out
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have successfully logged out.")
    else:
        messages.warning(request, "You are not logged in.")
    
    return redirect('userauth:login')
