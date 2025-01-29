from email.headerregistry import Group
from profile import Profile
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .forms import  AdForm, AdImageForm, AssignRoleForm, CategoryForm, CreateRoleForm, ProductForm, UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model, logout  # Correct way to reference the user model
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncHour
from core.models import  Ad, Address, CartOrderItems, Category, Vendor, Product, CartOrder
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.db.models import Sum
import calendar  # Ensure this is imported at the top
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.http import HttpResponseNotAllowed
from .forms import ProductEditForm
from django.contrib.auth.models import Group, Permission
from .forms import GroupPermissionForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from core.models import UserAction, Navbar
from .forms import NavbarForm


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



@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin', 'Editor'])

def admindashboard(request):
    # Restrict access to superusers only
    # if not request.user.is_superuser:
    #     return redirect('userauth:unauthorized')

    # Get all orders (remove user=request.user if admin should see all orders)
    orders_list = CartOrder.objects.all().order_by("-id")
    add = Address.objects.filter(user=request.user)

    # Calculate Total Sales Today (for all orders)
    total_sales_today = (
        CartOrder.objects.filter(order_date__date=timezone.now().date())
        .aggregate(total=Sum('price'))['total'] or 0
    )

    # Calculate Current Month Sales (for all orders)
    current_month = timezone.now().month
    current_month_sales = (
        CartOrder.objects.filter(order_date__month=current_month)
        .aggregate(total=Sum('price'))['total'] or 0
    )

    # Calculate Average Monthly Sales (for all orders)
    monthly_sales = (
        CartOrder.objects.annotate(month=ExtractMonth("order_date"))
        .values("month")
        .annotate(total_sales=Sum("price"))
        .values_list("total_sales", flat=True)
    )
    average_sales = sum(monthly_sales) / len(monthly_sales) if monthly_sales else 0

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
    

    return render(request, 'userauth/admindashboard.html', context, 
    )


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
@allowed_users(allowed_roles=['Admin'])
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('userauth:product_management')


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
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
    # if not request.user.is_superuser:
    #     return redirect('userauth:unauthorized')
    orders = CartOrder.objects.all()
    return render(request, 'userauth/orders.html', {'orders': orders})

def order_view(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'userauth/order_view.html', context)

from .forms import OrderEditForm
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
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
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def order_delete(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(CartOrder, id=order_id)
        order.delete()
        return redirect('userauth:orders')
    return HttpResponseNotAllowed(['POST'])
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
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

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
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




@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin', 'Editor'])

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

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def category_detail(request, category_id):
    # Get the category by ID
    category = get_object_or_404(Category, id=category_id)
    # Get all products in this category using the correct related_name
    products = category.products.all()
    return render(request, 'userauth/category_detail.html', {'category': category, 'products': products})

def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        return redirect('userauth:category_list')  # Redirect to the categories list page
    return HttpResponseNotAllowed(['POST'])
def category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('userauth:category_list')  # Redirect to categories list page
    else:
        form = CategoryForm(instance=category)
    return render(request, 'userauth/category_edit.html', {'form': form, 'category': category})

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def products(request):
    # Get all products
    products = Product.objects.all()

    # Handle form submission for creating new product
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  # Don't save to the database yet
            product.updated_by = request.User  # Set updated_by to the current user
            product.save()  # Now save to the database
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

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def navbars(request):
    # Get all navbars
    navbars = Navbar.objects.all()

    # Handle form submission for creating a new navbar item
    if request.method == 'POST':
        form = NavbarForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new navbar item
            return redirect('userauth:navbars')  # Redirect to the navbar list after saving
    else:
        form = NavbarForm()

    return render(request, 'userauth/navbars.html', {'navbars': navbars, 'form': form})


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def navbar_view(request, navbar_id):
    navbar = get_object_or_404(Navbar, id=navbar_id)
    return render(request, 'userauth/navbar_view.html', {'navbar': navbar})


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def navbar_edit(request, navbar_id):
    navbar = get_object_or_404(Navbar, id=navbar_id)

    if request.method == 'POST':
        form = NavbarForm(request.POST, instance=navbar)
        if form.is_valid():
            form.save()  # Save the updated navbar item
            return redirect('userauth:navbars')  # Redirect to navbar list after saving
    else:
        form = NavbarForm(instance=navbar)  # Pre-fill form with current navbar data

    return render(request, 'userauth/navbar_edit.html', {'form': form, 'navbar': navbar})


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def navbar_delete(request, navbar_id):
    if request.method == "POST":
        navbar = get_object_or_404(Navbar, id=navbar_id)
        navbar.delete()
        return redirect('userauth:navbars')
    return HttpResponseNotAllowed(['POST'])
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def manage_roles(request):
    if request.method == 'POST':
        assign_role_form = AssignRoleForm(request.POST)
        create_role_form = CreateRoleForm(request.POST)

        if 'create_role' in request.POST:  # If Create Role button is pressed
            if create_role_form.is_valid():
                role_name = create_role_form.cleaned_data['role_name']
                group = Group.objects.create(name=role_name)  # Create the new group
                return redirect('userauth:manage_roles')  # Redirect to refresh the page and show the new role

        elif 'assign_role' in request.POST:  # If Assign Role button is pressed
            if assign_role_form.is_valid():
                user = assign_role_form.cleaned_data['user']
                group = assign_role_form.cleaned_data['group']
                user.groups.add(group)  # Assign the selected group to the user
                return redirect('userauth:manage_roles')  # Redirect to refresh the page

    else:
        assign_role_form = AssignRoleForm()
        create_role_form = CreateRoleForm()

    return render(request, 'userauth/manage_roles.html', {
        'assign_role_form': assign_role_form,
        'create_role_form': create_role_form,
    })



# def advertisement(request):
#     # Fetch all advertisements
#     advertisement = Advertisement.objects.all()

#     context = {
#         'advertisement': advertisement,
#     }

#     return render(request, 'userauth/advertisement.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from core.models import Ad
from django.contrib import messages
from core.models import Ad, Adimage  # Import your models
from .forms import AdForm, AdImageForm  # Import your forms
def ad_list(request):
    ads = Ad.objects.all()
    return render(request, 'userauth/ad_list.html', {'ad': ads})


# Edit an ad (change image or status)from django.shortcuts import render, get_object_or_404, redirect


def ad_edit(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    # Fetch all images related to the ad
    ad_images = ad.images.all()  # Using related_name 'images' from Adimage model

    if request.method == 'POST':
        # Handle Ad form and AdImage form separately
        ad_form = AdForm(request.POST, request.FILES, instance=ad)  # For updating Ad (status, image, etc.)
        ad_image_form = AdImageForm(request.POST, request.FILES)  # For uploading new images

        # Validate Ad form first
        if ad_form.is_valid():
            ad_form.save()  # Save the Ad form

            # Now handle the AdImageForm separately for new image uploads
            if ad_image_form.is_valid() and 'image' in request.FILES:
                new_ad_image = ad_image_form.save(commit=False)
                new_ad_image.Ad = ad  # Link new image to the Ad
                new_ad_image.save()

            messages.success(request, 'Ad updated successfully!')
            return redirect('userauth:ad_list')

        else:
            # Handle errors for Ad form and AdImage form
            messages.error(request, 'There was an error updating the Ad. Please check the form data.')
            print(ad_form.errors)  # Debugging: Print form errors
            print(ad_image_form.errors)  # Debugging: Print image form errors

    else:
        # Prepopulate the forms with existing data
        ad_form = AdForm(instance=ad)
        ad_image_form = AdImageForm()

    return render(request, 'userauth/ad_edit.html', {
        'ad_form': ad_form,
        'ad_image_form': ad_image_form,
        'ad': ad,
        'ad_images': ad_images,  # Pass existing images to the template
    })



# Delete an ad
def ad_delete(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    if request.method == "POST":
        ad.delete()  # Delete the ad and associated images
        messages.success(request, 'Ad deleted successfully')
        return redirect('userauth:ad_list')  # Ensure this is correct

    return HttpResponseNotAllowed(['POST'])

@csrf_protect
# @allowed_users(allowed_roles=['Admin'])
@login_required
def edit_content(request):
    if request.user.groups.filter(name='Editor').exists():
        # Only editors can access this page
        # Your logic here for editors
        return render(request, 'userauth/edit_page.html')
    else:
        return HttpResponseForbidden("You do not have permission to edit.")
    
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def manage_group_permissions(request):
    groups = Group.objects.all()
    permissions = Permission.objects.all()

    if request.method == "POST":
        form = GroupPermissionForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            permissions = form.cleaned_data['permissions']
            group.permissions.set(permissions)  # Update group permissions
            group.save()
            return redirect('userauth/manage_group_permissions')
    else:
        form = GroupPermissionForm()

    return render(request, 'userauth/manage_group_permissions.html', {
        'groups': groups,
        'permissions': permissions,
        'form': form
    })



@staff_member_required
def activity_log_view(request):
    return redirect('admin:index')

from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from core.models import Product, Category, UserAction

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    UserAction.objects.create(user=user, action_type='LOGIN', description='User logged in.')

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    UserAction.objects.create(user=user, action_type='LOGOUT', description='User logged out.')

@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    user = instance.updated_by or None
    if created:
        description = f'Product "{instance.title}" created by {user}' if user else f'Product "{instance.title}" created.'
        action_type = 'PRODUCT_CREATED'
    else:
        description = f'Product "{instance.title}" updated by {user}' if user else f'Product "{instance.title}" updated.'
        action_type = 'PRODUCT_UPDATED'

    if user:
        UserAction.objects.create(user=user, action_type=action_type, description=description)

@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    user = instance.updated_by or None
    description = f'Product "{instance.title}" deleted by {user}' if user else f'Product "{instance.title}" deleted.'

    if user:
        UserAction.objects.create(user=user, action_type='PRODUCT_DELETED', description=description)

@receiver(post_save, sender=Category)
def log_category_save(sender, instance, created, **kwargs):
    user = instance.updated_by or None
    if created:
        description = f'Category "{instance.title}" created by {user}' if user else f'Category "{instance.title}" created.'
        action_type = 'CATEGORY_CREATED'
    else:
        description = f'Category "{instance.title}" updated by {user}' if user else f'Category "{instance.title}" updated.'
        action_type = 'CATEGORY_UPDATED'

    if user:
        UserAction.objects.create(user=user, action_type=action_type, description=description)

@receiver(post_delete, sender=Category)
def log_category_delete(sender, instance, **kwargs):
    user = instance.updated_by or None
    description = f'Category "{instance.title}" deleted by {user}' if user else f'Category "{instance.title}" deleted.'

    if user:
        UserAction.objects.create(user=user, action_type='CATEGORY_DELETED', description=description)



def user_activity(request):
    actions = UserAction.objects.all().order_by('-timestamp')  # Fetch all actions, ordered by timestamp (latest first)
    context = {
        'actions': actions,
    }
    return render(request, 'userauth/user_activity.html', context)