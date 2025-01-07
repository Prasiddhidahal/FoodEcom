from profile import Profile
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .forms import CategoryForm, ProductForm, UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model, logout  # Correct way to reference the user model
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncHour
from core.models import Address, CartOrderItems, Category, Vendor, Product, CartOrder
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.db.models import Sum
import calendar  # Ensure this is imported at the top
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseNotAllowed
from .forms import ProductEditForm

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
def admindashboard(request):
    # Restrict access to superusers only
    if not request.user.is_superuser:
        return redirect('userauth:unauthorized')

    # Get orders for the logged-in user
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    add = Address.objects.filter(user=request.user)

    # Calculate Total Sales Today
    total_sales_today = (
        CartOrder.objects.filter(user=request.user, order_date__date=timezone.now().date())
        .aggregate(total=Sum('price'))['total'] or 0
    )

    # Calculate Current Month Sales
    current_month = timezone.now().month
    current_month_sales = (
        CartOrder.objects.filter(user=request.user, order_date__month=current_month)
        .aggregate(total=Sum('price'))['total'] or 0
    )

    # Calculate Average Monthly Sales
    monthly_sales = (
        CartOrder.objects.filter(user=request.user)
        .annotate(month=ExtractMonth("order_date"))
        .values("month")
        .annotate(total_sales=Sum("price"))
        .values_list("total_sales", flat=True)
    )
    if monthly_sales:
        average_sales = sum(monthly_sales) / len(monthly_sales)
    else:
        average_sales = 0

    # Prepare data for the chart
    orders = (
        CartOrder.objects.annotate(month=ExtractMonth("order_date"))
        .values('month')
        .annotate(count=Count("id"))
        .values("month", "count")
    )
    month = []
    total_orders = []
    for order in orders:
        month_name = calendar.month_name[order['month']]  # Correct usage of calendar.month_name
        month.append(month_name)
        total_orders.append(order['count'])

    # Handle adding a new address
    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile
        )
        messages.success(request, "Address Added Successfully")

    context = {
        "orders_list": orders_list,
        "orders": orders,
        "address": add,
        "month": month,
        "total_orders": total_orders,
        "total_sales_today": total_sales_today,
        "current_month_sales": current_month_sales,
        "average_sales": average_sales,
    }

    return render(request, 'userauth/admindashboard.html', context)





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

def products(request):
    return render(request, 'userauth/products.html')

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def orders(request):
    if not request.user.is_superuser:
        return redirect('userauth:unauthorized')
    orders = CartOrder.objects.all()
    return render(request, 'userauth/orders.html', {'orders': orders})

def order_view(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'userauth/order_view.html', context)

from .forms import OrderEditForm

def order_edit(request, order_id):
    # Fetch the order to be edited
    order = get_object_or_404(CartOrder, id=order_id)
    
    # Get the cart items for the current order
    cart_items = CartOrderItems.objects.filter(order=order)  # Assuming CartItem has a ForeignKey to CartOrder
    
    # Calculate total number of items ordered by summing the quantities of cart items
    total_items_ordered = sum(item.qty for item in cart_items)
    
    # If the form is being submitted
    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()  # Save the updated order
            return redirect('userauth:orders')  # Redirect to view page after saving
    else:
        form = OrderEditForm(instance=order)  # Pre-fill form with current order data
    
    context = {
        'form': form,
        'order': order,
        'cart_items': cart_items,  # Pass cart items to the template
        'total_items_ordered': total_items_ordered,  # Pass the total number of items ordered
    }

    return render(request, 'userauth/order_edit.html', context)

def order_delete(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(CartOrder, id=order_id)
        order.delete()
        return redirect('userauth:orders')
    return HttpResponseNotAllowed(['POST'])
def customer_orders(request):
    # Get all users who have placed orders
    users = User.objects.all()
    
    # Initialize a list to store customer order details
    customer_orders = []
    
    # Loop through users and get their orders and address
    for user in users:
        orders = CartOrder.objects.filter(user=user).order_by('-order_date')
        address = Address.objects.filter(user=user).first()  # Get the user's address (if it exists)
        
        # Only add customers who have orders
        if orders:
            customer_orders.append({
                'user': user,
                'orders': orders,
                'address': address  # Add address to the context
            })

    context = {
        'customer_orders': customer_orders
    }

    return render(request, 'userauth/customer.html', context)


def customer_order_details(request, user_id):
    # Get the user object by user_id
    user = get_object_or_404(User, id=user_id)

    # Get all the orders for this user
    orders = CartOrder.objects.filter(user=user).order_by('-order_date')

    context = {
        'user': user,
        'orders': orders
    }

    return render(request, 'userauth/customer_order_details.html', context)


def add_product(request):
    return render(request, 'userauth/add_product.html')





def category_list(request):
    categories = Category.objects.all()

    # Handling the form submission for creating new category
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')

        # Create and save the new category
        new_category = Category.objects.create(
            title=title,
            image=image
        )
        # Redirect to the category list page after adding the new category
        return redirect('userauth:category_list')  # Use URL name instead of a direct file reference

    return render(request, 'userauth/categories.html', {'categories': categories})

def category_detail(request, category_id):
    # Get the category by ID
    category = get_object_or_404(Category, id=category_id)
    # Get all products in this category using the correct related_name
    products = category.products.all()
    return render(request, 'userauth/category_detail.html', {'category': category, 'products': products})


@csrf_protect
# @login_required
# @allowed_users(allowed_roles=['Admin'])
def products(request):
    if not request.user.is_superuser:
        return redirect('userauth:unauthorized')
    
    # Get all products
    products = Product.objects.all()

    # Handle form submission for creating new product
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('userauth:products')  # Redirect to the product list after saving

    else:
        form = ProductForm()

    return render(request, 'userauth/products.html', {'products': products, 'form': form})


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'userauth/product_view.html', context)

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductEditForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()  # Save the updated product
            return redirect('userauth:products')  # Redirect to products list after saving
    else:
        form = ProductEditForm(instance=product)  # Pre-fill form with current product data
    
    context = {
        'form': form,
        'product': product,
    }
    
    return render(request, 'userauth/product_edit.html', context)

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def product_delete(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return redirect('userauth:products')
    return HttpResponseNotAllowed(['POST'])