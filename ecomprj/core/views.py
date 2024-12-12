from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, Wishlist, Address
# views here.
from django.shortcuts import  get_object_or_404
from django.core.paginator import Paginator
from taggit.models import Tag
from django.db.models import Avg
from ecomprj.forms import ProductReviewForm
def index(request):
    products=Product.objects.filter(product_status="published")
    categories = Category.objects.all()
    Vendors = Vendor.objects.all()
    context={
        'products':products,
        'categories': categories,
        'vendors': Vendors
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

def shop(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'core/shop-grid.html', context)

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


def pages1(request, pid):
    product = get_object_or_404(Product, id=pid)

    # Fetch related products from the same category, excluding the current product
    related_products = Product.objects.filter(
        category=product.category,
        product_status="published"
    ).exclude(id=pid)[:4]  # Limit to 4 related products

    products_images = product.products_images.all()
    address = Address.objects.filter(user=request.user)
    review = ProductReview.objects.filter(product=product)

    # Get the average rating and handle the case when there are no reviews
    average_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    review_form=ProductReviewForm()
    # Set a default value of 0 if there are no reviews
    if average_rating is None:
        average_rating = 0

    # Create a star range for 1 to 5 stars
    star_range = [1, 2, 3, 4, 5]

    context = {
        'review_form': review_form,
        'product': product,
        'review': review,
        'related_products': related_products,
        'products_images': products_images,
        'average_rating': average_rating,
        'star_range': star_range,  # Pass the range to the template
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
    try:
        product = Product.objects.get(id=pid)

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'bool': False, 'message': 'User must be logged in'}, status=400)

        # Check if the user has already reviewed this product
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            return JsonResponse({'bool': False, 'message': 'You have already reviewed this product'}, status=400)

        # Create a review
        review_text = request.POST.get('review')
        rating = request.POST.get('rating')

        if not review_text or not rating:
            return JsonResponse({'bool': False, 'message': 'Review and rating are required'}, status=400)

        user = request.user
        review = ProductReview.objects.create(
            product=product,
            user=user,
            review=review_text,
            rating=rating
        )

        # Calculate the average rating for the product
        average_reviews = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))

        context = {
            'review': review_text,
            'user': user.username,
            'rating': rating,
            'average_reviews': average_reviews.get('rating__avg', 0)
        }

        return JsonResponse({'bool': True, 'review': context, 'average_reviews': context['average_reviews']})

    except Product.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Product not found'}, status=404)

    except Exception as e:
        return JsonResponse({'bool': False, 'message': str(e)}, status=500)