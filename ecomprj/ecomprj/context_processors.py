from core.models import CartOrder, Category, Address, Vendor, Product
from django.db.models import Max, Min
from calendar import month_name
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from core.models import Navbar
def navbar_items(request):
    navbars = Navbar.objects.filter(status='Active')
    return {'navbars': navbars}
def default(request):
    # Initialize the cart total amount and cart count
    cart_total_amount = 0
    cart_count = 0

    # Initialize months and monthly_sales to avoid UnboundLocalError
    months = []
    monthly_sales = []

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve the address for the authenticated user
        address = Address.objects.filter(user_id=request.user.id).first()
    else:
        address = None  # For anonymous users, set address to None or handle appropriately

    # Retrieve categories and vendors
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))

    # Calculate cart total amount and cart count if 'cart_data_object' exists in the session
    if 'cart_data_object' in request.session:
        cart_data = request.session['cart_data_object']
        # Calculate the total amount by summing up price * quantity for each item
        cart_total_amount = sum(float(item['price']) * int(item['qty']) for item in cart_data.values())
        # Calculate the total count of products by summing up the quantities
        cart_count = sum(int(item['qty']) for item in cart_data.values())
        
        # Retrieve monthly sales data
        monthly_sales_data = (
            CartOrder.objects.annotate(month=TruncMonth('order_date'))
            .values('month')
            .annotate(total_sales=Sum('price'))
            .order_by('month')
        )
        
        # Populate months and monthly_sales
        months = [month_name[sale['month'].month] for sale in monthly_sales_data]
        monthly_sales = [sale['total_sales'] or 0 for sale in monthly_sales_data]

    # Return the context with address, categories, vendors, price range, cart total amount, and cart count
    return {
        'address': address,
        'categories': categories,
        'vendors': vendors,
        'min_max_price': min_max_price,
        'cart_total_amount': cart_total_amount,  # Adding cart total amount to the context
        'cart_count': cart_count,
        'months': months,
        'monthly_sales': monthly_sales,
    }
