from core.models import Category, Address

def default(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve the address for the authenticated user
        address = Address.objects.filter(user_id=request.user.id).first()
        
        # Retrieve categories (adjust based on your requirement, e.g., active categories)
        categories = Category.objects.all()  # Modify query as needed (e.g., filter based on conditions)
    else:
        address = None  # For anonymous users, set address to None or handle appropriately
        categories = Category.objects.all()  # Assuming categories are available to everyone (authenticated or not)
    
    # Return the context with both address and categories
    return {
        'address': address,
        'categories': categories
    }
