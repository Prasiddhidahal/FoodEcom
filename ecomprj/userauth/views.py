from email.headerregistry import Group
from profile import Profile
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .forms import  About_companyForm, AdForm, AdImageForm, AssignRoleForm, CategoryForm, CreateRoleForm, FooterForm, ProductForm, UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model, logout  
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncHour
from core.models import  About_company, Ad, Address, CartOrderItems, Category, Footer, Slider, Vendor, Product, CartOrder
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.db.models import Sum
import calendar  
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.http import HttpResponseNotAllowed
from .forms import ProductEditForm
from django.contrib.auth.models import Group, Permission
from .forms import GroupPermissionForm
from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from core.models import UserAction, Navbar
from .forms import NavbarForm
from .forms import OrderEditForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from core.models import Ad
from django.contrib import messages
from core.models import Ad, Adimage
from .forms import AdForm, AdImageForm 
from django.contrib.auth.models import Group, Permission
from .forms import GroupPermissionForm
from django.db.models import Count, Avg
User = get_user_model()  

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
            new_user = authenticate(username=form.cleaned_data['email'],  
                                    password=form.cleaned_data['password1'])

            
            if new_user is not None:
                login(request, new_user)
                return redirect('core:index')  
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, 'userauth/register.html', context)

@csrf_protect
def user_login(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in.")
        return redirect('core:index')

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.warning(request, f'No user found with the email {email}. Please try again.')
            return render(request, "userauth/login.html")

        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect("core:index")
        else:
            messages.warning(request, "Incorrect password. Please try again.")

    return render(request, "userauth/login.html")

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have successfully logged out.")
    else:
        messages.warning(request, "You are not logged in.")
    
    return redirect('userauth:login')

from django.db.models import Max
#start of admin pages
#admin dashboard
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin', 'Editor'])

def admindashboard(request):
    orders_list = CartOrder.objects.all().order_by("-id")
    add = Address.objects.filter(user=request.user)
    total_sales_today = (
        CartOrder.objects.filter(order_date__date=timezone.now().date())
        .aggregate(total=Sum('price'))['total'] or 0
    )
    current_month = timezone.now().month
    current_month_sales = (
        CartOrder.objects.filter(order_date__month=current_month)
        .aggregate(total=Sum('price'))['total'] or 0
    )
    
    # Calculated Average Monthly Sales 
    monthly_sales = (
        CartOrder.objects.annotate(month=ExtractMonth("order_date"))
        .values("month")
        .annotate(total_sales=Sum("price"))
        .values_list("total_sales", flat=True)
    )
    average_sales = sum(monthly_sales) / len(monthly_sales) if monthly_sales else 0

    # Prepared data for the chart
    orders = (
        CartOrder.objects.annotate(month=ExtractMonth("order_date"))
        .values('month')
        .annotate(count=Count("id"))
        .values("month", "count")
    )
    month = []
    total_orders = []
    for order in orders:
        month_name = calendar.month_name[order['month']] 
        month.append(month_name)
        total_orders.append(order['count'])

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile
        )
        messages.success(request, "Address Added Successfully")
    
    top_rated_products = Product.objects.annotate(average_rating=Avg('reviews__rating')).order_by('-average_rating')[:5]
    
    top_selling_products = Product.objects.order_by('-sold_quantity')[:5]
    context = {
        "orders_list": orders_list,
        "orders": orders,
        "address": add,
        "month": month,
        "total_orders": total_orders,
        "total_sales_today": total_sales_today,
        "current_month_sales": current_month_sales,
        "average_sales": average_sales,
        'top_rated_products': top_rated_products,
        'top_selling_products': top_selling_products,
    }
    return render(request, 'userauth/admindashboard.html', context, 
    )

@csrf_protect
@login_required
def unauthorized(request):
    return render(request, 'userauth/unauthorized.html', {
        'message': 'You do not have permission to access this page.'
    })

def products(request):
    return render(request, 'userauth/products.html')

#order 
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def orders(request):
    orders = CartOrder.objects.all()
    return render(request, 'userauth/orders.html', {'orders': orders})

def order_view(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'userauth/order_view.html', context)

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def order_edit(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    cart_items = CartOrderItems.objects.filter(order=order)  
    total_items_ordered = sum(item.qty for item in cart_items)
    
    # If the form is being submitted
    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save() 
            return redirect('userauth:orders')  
    else:
        form = OrderEditForm(instance=order)  
    
    context = {
        'form': form,
        'order': order,
        'cart_items': cart_items,  
        'total_items_ordered': total_items_ordered,  
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
    users = User.objects.all()
    customer_orders = []

    for user in users:
        orders = CartOrder.objects.filter(user=user).order_by('-order_date')
        address = Address.objects.filter(user=user).first()  

        if orders:
            customer_orders.append({
                'user': user,
                'orders': orders,
                'address': address  
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

#category
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin', 'Editor'])

def category_list(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')

        new_category = Category.objects.create(
            title=title,
            image=image
        )
        return redirect('userauth:category_list') 
    return render(request, 'userauth/categories.html', {'categories': categories})

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()
    return render(request, 'userauth/category_detail.html', {'category': category, 'products': products})

def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        return redirect('userauth:category_list') 
    return HttpResponseNotAllowed(['POST'])
def category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('userauth:category_list')  
    else:
        form = CategoryForm(instance=category)
    return render(request, 'userauth/category_edit.html', {'form': form, 'category': category})

#products
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def products(request):
    products = Product.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  
            product.updated_by = request.user  
            product.save() 
            return redirect('userauth:products')   
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
            form.save()  
            return redirect('userauth:products')  
    else:
        form = ProductEditForm(instance=product)  
    
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

#dymanic navbar
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def navbars(request):
    navbars = Navbar.objects.all()

    if request.method == 'POST':
        form = NavbarForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('userauth:navbars')  
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
            form.save()  
            return redirect('userauth:navbars') 
    else:
        form = NavbarForm(instance=navbar)  

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

#roles
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def manage_roles(request):
    if request.method == 'POST':
        assign_role_form = AssignRoleForm(request.POST)
        create_role_form = CreateRoleForm(request.POST)

        if 'create_role' in request.POST:  
            if create_role_form.is_valid():
                role_name = create_role_form.cleaned_data['role_name']
                group = Group.objects.create(name=role_name)  
                return redirect('userauth:manage_roles')  

        elif 'assign_role' in request.POST: 
            if assign_role_form.is_valid():
                user = assign_role_form.cleaned_data['user']
                group = assign_role_form.cleaned_data['group']
                user.groups.add(group) 
                return redirect('userauth:manage_roles')  

    else:
        assign_role_form = AssignRoleForm()
        create_role_form = CreateRoleForm()

    return render(request, 'userauth/manage_roles.html', {
        'assign_role_form': assign_role_form,
        'create_role_form': create_role_form,
    })

#ads
def ad_list(request):
    ads = Ad.objects.all()
    return render(request, 'userauth/ad_list.html', {'ad': ads})

def ad_edit(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    ad_images = ad.images.all()  

    if request.method == 'POST':
        ad_form = AdForm(request.POST, request.FILES, instance=ad) 
        ad_image_form = AdImageForm(request.POST, request.FILES)  

        if ad_form.is_valid():
            ad_form.save() 

            if ad_image_form.is_valid() and 'image' in request.FILES:
                new_ad_image = ad_image_form.save(commit=False)
                new_ad_image.Ad = ad  
                new_ad_image.save()

            messages.success(request, 'Ad updated successfully!')
            return redirect('userauth:ad_list')

        else:
            messages.error(request, 'There was an error updating the Ad. Please check the form data.')
            print(ad_form.errors)  
            print(ad_image_form.errors) 

    else:
        ad_form = AdForm(instance=ad)
        ad_image_form = AdImageForm()

    return render(request, 'userauth/ad_edit.html', {
        'ad_form': ad_form,
        'ad_image_form': ad_image_form,
        'ad': ad,
        'ad_images': ad_images,  
    })

#slidersfrom django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Slider
from userauth.forms import SliderForm  # Ensure you have a form to handle slider edits
from userauth.decorators import allowed_users  # Ensure this decorator exists

@login_required
@allowed_users(allowed_roles=['Admin'])
def slider_list(request):
    sliders = Slider.objects.all()[:4]  # Limit to 4 sliders
    return render(request, 'userauth/slider_list.html', {'sliders': sliders})

@login_required
@allowed_users(allowed_roles=['Admin'])
def slider_edit(request, slider_id):
    slider = get_object_or_404(Slider, id=slider_id)
    
    if request.method == 'POST':
        slider_form = SliderForm(request.POST, request.FILES, instance=slider)  # Handle slider form with image

        if slider_form.is_valid():
            slider_form.save()  # Save the updated slider
            messages.success(request, 'Slider updated successfully!')
            return redirect('userauth:slider_list')
        else:
            messages.error(request, 'There was an error updating the slider. Please check the form data.')

    else:
        slider_form = SliderForm(instance=slider)  # Prepopulate form with the existing slider

    return render(request, 'userauth/slider_edit.html', {
        'slider_form': slider_form,
        'slider': slider,
    })


#manage group permissions  
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
            group.permissions.set(permissions)  
            group.save()
            return redirect('userauth/manage_group_permissions')
    else:
        form = GroupPermissionForm()

    return render(request, 'userauth/manage_group_permissions.html', {
        'groups': groups,
        'permissions': permissions,
        'form': form
    })

#activity view but isnt working
@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def activity_log_view(request):
    return render(request, 'userauth/activity_log.html')

#activity log tried but only login logout shown
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
    actions = UserAction.objects.all().order_by('-timestamp')  
    context = {
        'actions': actions,
    }
    return render(request, 'userauth/user_activity.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .forms import FooterForm
from core.models import Footer
from .decorators import allowed_users

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def footers(request):
    footers = Footer.objects.all()

    if request.method == 'POST':
        form = FooterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('userauth:footers')
    else:
        form = FooterForm()

    return render(request, 'userauth/footer.html', {'footers': footers, 'form': form})

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def footer_view(request, footer_id):
    footer = get_object_or_404(Footer, id=footer_id)
    return render(request, 'userauth/footer_view.html', {'footer': footer})

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def footer_edit(request, footer_id):
    footer = get_object_or_404(Footer, id=footer_id)

    if request.method == 'POST':
        form = FooterForm(request.POST, instance=footer)
        if form.is_valid():
            form.save()
            return redirect('userauth:footers')
    else:
        form = FooterForm(instance=footer)

    return render(request, 'userauth/footer_edit.html', {'form': form, 'footer': footer})

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def footer_delete(request, footer_id):
    if request.method == "POST":
        footer = get_object_or_404(Footer, id=footer_id)
        footer.delete()
        return redirect('userauth:footers')
    return HttpResponseNotAllowed(['POST'])

@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def about_company(request):
    about_company = get_object_or_404(About_company, id=1)  # Assuming there's only one About Company record
    if request.method == 'POST':
        form = About_companyForm(request.POST, request.FILES, instance=about_company)
        if form.is_valid():
            form.save()
            return redirect('userauth:about_company')
    else:
        form = About_companyForm(instance=about_company)
    return render(request, 'userauth/about_company.html', {'form': form})


@csrf_protect
@login_required
@allowed_users(allowed_roles=['Admin'])
def about_company_edit(request):
    about_company = get_object_or_404(About_company, id=1)  # Assuming there's only one "About Company" record
    if request.method == 'POST':
        form = About_companyForm(request.POST, request.FILES, instance=about_company)
        if form.is_valid():
            form.save()
            return redirect('core:about_company')  # Redirect to the actual about page after edit
    else:
        form = About_companyForm(instance=about_company)
    return render(request, 'userauth/edit_about_company.html', {'form': form})