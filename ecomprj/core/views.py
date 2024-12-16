from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, Wishlist, Address
# views here.
from django.shortcuts import  get_object_or_404
from django.core.paginator import Paginator
from taggit.models import Tag
from django.db.models import Avg
from ecomprj.forms import ProductReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string	
def index(request):
    products=Product.objects.filter(product_status="published")
    categories = Category.objects.all()
    Vendors = Vendor.objects.all()
    latest_products = Product.objects.filter(
        product_status="published", in_stock=True
    ).order_by('-mfd')[:6]
    top_rated_products = Product.objects.filter(
    product_status="published"
).annotate(
    average_rating=Avg('reviews__rating')  # Calculate the average rating from related reviews
).filter(
    average_rating__isnull=False  # Exclude products with no ratings
).order_by('-average_rating')[:3]

    context={
        'products':products,
        'categories': categories,
        'vendors': Vendors,
        'latest_products': latest_products,
        'top_rated_products': top_rated_products,
    }

    return render(request, 'core/index.html', context)

def categories(request):
    # Get all categories
    products=Product.objects.filter(product_status="published")
    categories = Category.objects.all()

    # Calculate the number of products for each category
    for category in categories:
        category.product_count = Product.objects.filter(category=category).count()

    context = {
        'categories': categories,
        'products':products,
    }

    return render(request, 'core/category_products.html', context)

def category_product_list(request, cid):
    # Get the category using the 'cid' which is a string
    category = Category.objects.get ( cid=cid)  # Assuming 'cid' is a unique identifier (string)

    # Get all products in the category
    products = Product.objects.filter(product_status="published", category=category)
    
    context = {
        'category': category,
        'products': products,
    }

    return render(request, 'core/category_product_list.html', context)


def cart(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'core/shoping-cart.html', context)

def checkout(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'core/checkout.html', context)

def contact(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'core/contact.html', context)

def blog(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'core/blog.html', context)

def blog_details(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'core/blog-details.html', context)

def register(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'userauth/register.html', context)

def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        'vendors': vendors,
    }
    return render(request, 'core/vendor_list.html', context)

def vendor_products(request, vid):
    # Change 'id' to the correct field, like 'slug' or 'vid'
    vendor = get_object_or_404(Vendor, vid=vid)  # Using 'vid' as the field name

    # Get all products associated with the vendor
    products = Product.objects.filter(vendor=vendor, product_status="published")

    context = {
        'vendor': vendor,
        'products': products,
    }

    return render(request, 'core/vendor_products.html', context)
def shop(request):
    categories = Category.objects.all()
    latest_products = Product.objects.filter(
        product_status="published", in_stock=True
    ).order_by('-mfd')[:6]
    vendors = Vendor.objects.all()  # Fetching all vendors
    tags = Tag.objects.all()  # Fetching all tags for the filter

    tag_slug = request.GET.get('tag')  # Get tag slug from query parameters

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)  # Get the tag or return 404
        latest_products = latest_products.filter(tags__in=[tag])  # Filter products by the tag

    context = {
        'categories': categories,
        'latest_products': latest_products,
        'vendors': vendors,  # Pass vendors to the context
        'tags': tags,  # Pass tags to the context
        'selected_tag': tag_slug  # Pass selected tag to highlight it
    }
    return render(request, 'core/shop-grid.html', context)



def pages1(request, pid):
    # Fetch the product by its ID
    product = get_object_or_404(Product, id=pid)

    # Fetch related products from the same category, excluding the current product
    related_products = Product.objects.filter(
        category=product.category,
        product_status="published"
    ).exclude(id=pid)[:4]  # Limit to 4 related products

    # Fetch product images
    products_images = product.products_images.all()

    # Initialize the address variable
    address = None
    if request.user.is_authenticated:
        # Fetch the address for the authenticated user, or None if not found
        address = Address.objects.filter(user=request.user).first()

    # Fetch product reviews
    ReviewForm = ProductReviewForm()

    # Calculate the average rating, defaulting to 0 if there are no reviews
    average_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0

    # Create a star range for display purposes (1 to 5 stars)
    star_range = [1, 2, 3, 4, 5]

    # Prepare the context for rendering the template
    context = {
        'review_form': ProductReviewForm(),
        'product': product,
        'related_products': related_products,
        'products_images': products_images,
        'average_rating': average_rating,
        'star_range': star_range,  # Pass the range to the template
        'address': address  # Pass the user's address if available
    }

    return render(request, 'core/pages1.html', context)

def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)  # Get the tag or return 404
        products = products.filter(tags__in=[tag])  # Filter products by the tag

    context = {
        'products': products,
        'tag': tag,
    }
    return render(request, 'core/tag.html', context)

def add_review(request, pid):
    product = get_object_or_404(Product, id=pid)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ProductReviewForm(request.POST)
        
        if form.is_valid():
            # Check if the user has already reviewed this product
            if ProductReview.objects.filter(product=product, user=request.user).exists():
                return JsonResponse({'bool': False, 'message': 'You have already reviewed this product'}, status=400)
            
            # Save the review
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            # Optionally, calculate and update the average rating here
            average_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))
            product.average_rating = average_rating.get('rating__avg', 0)
            product.save()

            return JsonResponse({'bool': True, 'message': 'Review submitted successfully!'})

        else:
            return JsonResponse({'bool': False, 'message': 'Invalid form submission'}, status=400)
    
    else:
        form = ProductReviewForm()
        
    context = {
        'product': product,
        'review_form': form,
    }
    return render(request, 'core/pages.html', context)

def search_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(title__icontains=query)# if fresh pear then if we type pear or fre or esh then it will show the result
    context = {
        'products': products,
        'query': query
    }
    return render(request, 'core/search.html', context)

def filter_product(request):
    category_slugs = request.GET.getlist('category[]')  # List of category slugs (not IDs)
    vendor_ids = request.GET.getlist('vendor[]')  # List of vendor IDs
    tag_ids = request.GET.getlist('tag[]')  # List of tag IDs

    # Use .get() to avoid KeyError and provide default values
    min_price = request.GET.get('min_price', 0)  # Default min_price to 0
    max_price = request.GET.get('max_price', 1000000)  # Default max_price to a very large number

    try:
        min_price = float(min_price)
        max_price = float(max_price)
    except ValueError:
        min_price = 0
        max_price = 1000000

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()

    # Filter by price range
    products = products.filter(price__gte=min_price, price__lte=max_price)

    # Filter by category slugs if provided
    if category_slugs:
        products = products.filter(category__slug__in=category_slugs).distinct()

    # Filter by vendor IDs if provided
    if vendor_ids:
        products = products.filter(vendor__id__in=vendor_ids).distinct()

    # Filter by tag IDs if provided
    if tag_ids:
        products = products.filter(tags__id__in=tag_ids).distinct()

    context = {
        "products": products,
    }
    data = render_to_string("async/product-list.html", context)

    return JsonResponse({
        "data": data,
    })
def filter_product(request):
    
    category_cids = request.GET.getlist('category[]')  # List of category IDs (not slugs)
    vendor_vids = request.GET.getlist('vendor[]')  # List of vendor IDs
    tag_slugs = request.GET.getlist('tag[]')
    
    # Use .get() to avoid KeyError and provide default values
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)

    # Convert min_price and max_price to floats if provided
    if min_price is not None:
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = None  # Handle invalid values gracefully

    if max_price is not None:
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = None  # Handle invalid values gracefully

    # Start with all products that are published
    products = Product.objects.filter(product_status="published").order_by("-id").distinct()

    # Apply price filtering if min_price and max_price are provided
    if min_price is not None and max_price is not None:
        products = products.filter(price__gte=min_price, price__lte=max_price)
    elif min_price is not None:
        products = products.filter(price__gte=min_price)
    elif max_price is not None:
        products = products.filter(price__lte=max_price)

    # Filter by category IDs if provided
    if category_cids:
        products = products.filter(category__cid__in=category_cids).distinct()

    # Filter by vendor IDs if provided
    if vendor_vids:
        products = products.filter(vendor__vid__in=vendor_vids).distinct()

    # Filter by tag slugs if provided
    if tag_slugs:
        products = products.filter(tags__slug__in=tag_slugs).distinct()

    # Fetch all tags to populate the filter form
    tags = Tag.objects.all()

    context = {
        "products": products,
        "tags": tags,  # Pass the tags to the context
    }
    data = render_to_string("core/async/product-list.html", context)

    return JsonResponse({
        "data": data,
    })
