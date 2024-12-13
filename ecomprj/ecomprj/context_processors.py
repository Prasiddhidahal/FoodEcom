from core.models import Category, Address

def default(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Use request.user.id to avoid passing the entire user object
        address = Address.objects.filter(user_id=request.user.id).first()  # Note the change to user_id
    else:
        address = None  # Or handle appropriately for anonymous users
    return {
        'address': address
    }


