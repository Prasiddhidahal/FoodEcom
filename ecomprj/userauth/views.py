from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model, logout  # Correct way to reference the user model
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncHour
from core.models import Vendor, Product, CartOrder
from django.db.models import Count, Sum

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




@login_required
@allowed_users(allowed_roles=['Admin'])
def vendordashboard(request):
    # Restrict access to superusers only
    if not request.user.is_superuser:
        return redirect('userauth:unauthorized')  

    # Current date to filter products, vendors, and orders created today
    now = timezone.now()
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Orders created today by hour
    orders_by_hour = CartOrder.objects.filter(order_date=start_time) \
        .order_by('order_date') \
        .annotate(hour=TruncHour('order_date')) \
        .values('hour') \
        .annotate(count=Count('id')) \
        .order_by('hour')

    # Vendors created today
    vendors_today = Vendor.objects.filter(date=start_time.date()).count()

    # Products added today
    products_today = Product.objects.filter(created_at__date=start_time.date()).count()

    # Total sales (sum of prices of all orders today)
    total_sales_today = CartOrder.objects.filter(order_date=start_time) \
        .aggregate(Sum('price'))['price__sum'] or 0

    # Data for charts (orders per hour)
    hours = list(range(0, 24))
    order_data = [0] * 24  # To store orders per hour

    # Fill in order data by hour
    for order in orders_by_hour:
        order_data[order['hour'].hour] = order['count']

    # Get total number of vendors, products, and orders
    total_vendors = Vendor.objects.count()
    total_products = Product.objects.count()
    total_orders = CartOrder.objects.count()

    context = {
        'hours': hours,
        'order_data': order_data,
        'vendors_today': vendors_today,
        'products_today': products_today,
        'total_sales_today': total_sales_today,
        'total_vendors': total_vendors,
        'total_products': total_products,
        'total_orders': total_orders,
    }

    return render(request, 'userauth/vendordashboard.html', context)


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def vendor_management(request):
    if not request.user.is_superuser:
        return redirect('userauth:unauthorized')
    vendors = Vendor.objects.all()
    return render(request, 'userauth/vendor_management.html', {'vendors': vendors})


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def delete_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.delete()
    return redirect('userauth:vendor_management')


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        vendor.title = request.POST['title']
        vendor.email = request.POST['email']
        vendor.phone = request.POST['phone']
        vendor.save()
        return redirect(reverse('vendor:vendor_management'))
    return render(request, 'userauth/edit_vendor.html', {'vendor': vendor})


@csrf_protect
@login_required
def product_management(request):
    if not request.user.is_superuser:
        return redirect('userauth:unauthorized')
    products = Product.objects.all()
    return render(request, 'userauth/product_management.html', {'products': products})


@csrf_protect
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('userauth:product_management')


@csrf_protect
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.title = request.POST['title']
        product.price = request.POST['price']
        product.stock_quantity = request.POST['stock_quantity']
        product.save()
        return redirect(reverse('vendor:product_management'))
    return render(request, 'userauth/edit_product.html', {'product': product})


@csrf_protect
@login_required
def unauthorized(request):
    return render(request, 'userauth/unauthorized.html', {
        'message': 'You do not have permission to access this page.'
    })