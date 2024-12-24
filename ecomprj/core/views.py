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
from django.db.models import Count, Avg
import uuid
import hmac
import hashlib
import hmac, hashlib,json,base64,requests
from django.conf import settings


# Function to generate HMAC SHA256 signature
def genSha256(key, message):
    key = key.encode('utf-8')
    message = message.encode('utf-8')

    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode('utf-8')

    return signature



def initiate_khalti(request):
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    return_url = request.POST.get('return_url')
   
    
    amount = request.POST.get('amount') 
    purchase_order_id = request.POST.get('purchase_order_id')
    user= request.user
    payload = json.dumps({
        "return_url": return_url,
        "website_url": "http://127.0.0.1:8000/",
        "amount": amount,
        "purchase_order_id": purchase_order_id,
        "purchase_order_name": "test",
        "customer_info": {
        "name": user.username,
        "email": user.email,
        "phone": "9800000001",
        # "phone": user.phone_number
        }
    })
    headers = {
        'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.text:
        try:
            new_res = response.json()  # This will safely parse JSON
        except ValueError as e:
            print("Error parsing JSON:", e)
            # Handle the error, possibly returning an error response to the user
    else:
        print("Empty response:", response.text)
    # new_res= json.loads(response.text)
    # dd(new_res)
    return redirect(new_res['payment_url'])
    

def khalti_verify(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    pidx= request.GET.get('pidx')
    headers = {
        'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload= json.dumps({
        'pidx':pidx
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    new_res= json.loads(response.text)
    
    # dd(new_res)
    if new_res['status'] == 'Completed':
        messages.success(request,"Payment completed successfully.")
        invoice(request)
    elif new_res['status'] == 'Pending':
        messages.warning(request,"Payment is still pending.")
    elif new_res['status'] == 'Initiated':
        messages.warning(request,"Payment has been initiated.")
    elif new_res['status'] == 'Refunded':
        messages.success(request,"Payment has been refunded.")
    elif new_res['status'] == 'Partially Refunded':
        messages.success(request,"Payment has been partially refunded.")
    elif new_res['status'] == 'Expired':
        messages.error(request,"Payment link has expired.")
    elif new_res['status'] == 'User canceled':
        messages.error(request,"Payment was canceled by the user.")
    else:
        messages.error(request,"Unknown payment status.")
    return redirect("core:index")

    




def verify_esewa(request):
    if request.method == 'GET':
        try:
            data = request.GET.get('data')
            decoded_data = base64.b64decode(data).decode('utf-8')
            map_data =json.loads(decoded_data)
            if map_data.get('status') == "PENDING":
                messages.warning(request,"The transaction is still pending.")
            elif map_data.get('status') == "COMPLETE":
                messages.success(request,"The transaction is complete.")
                invoice(request)
            elif map_data.get('status') == "FULL_REFUND":
                messages.success(request,"The transaction has been fully refunded.")
            elif map_data.get('status') == "PARTIAL_REFUND":
                messages.success(request,"The transaction has been partially refunded.")
            elif map_data.get('status') == "AMBIGUOUS":
                messages.warning(request,"The transaction status is ambiguous. Please contact support.")
            elif map_data.get('status') == "NOT_FOUND":
                messages.error(request,"The transaction was not found.")
            elif map_data.get('status') == "CANCELED":
                messages.error(request,"The transaction has been canceled.")
            elif map_data.get('status') == "Service is currently unavailable":
                messages.error(request,"The service is currently unavailable. Please try again later.")
            else:
                messages.error(request,"Unknown status.")
            return redirect("core:index")
        except Exception as e:
            print(e)
            messages.error(request,"The service is currently down please try again later or contact our representatives")
            return redirect("core:index")
@login_required
def checkout_view(request):

    cart_total_amount=0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += float(item['price']) * int(item['qty'])
        
    if request.method == 'POST':
        cart_total_amount=0
        if 'cart_data_obj' in request.session:
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += float(item['price']) * int(item['qty'])
            order = CartOrder.objects.create(
                user = request.user,
                price= cart_total_amount

            )
            for p_id, item in request.session['cart_data_obj'].items():
                cart_order_products = CartOrderItems.objects.create(
                    order = order,
                    invoice_no = "INVOICE_NO_"+str(order.id),
                    item=item['title'],
                    image=item['image'],
                    qty=item['qty'],
                    price=item['price'],
                    total=float(item['qty']) * float(item['price']),
                    


                )
        pay_type = request.POST.get('pay_type')
        if pay_type == 'esewa':
            uid = uuid.uuid4()
            tax_amount = 0 
            amount = cart_total_amount
            total_amount = amount + tax_amount
            data_to_sign = f"total_amount={total_amount},transaction_uuid={uid},product_code={settings.ESEWA_PRODUCT_CODE}"
            result= genSha256(settings.ESEWA_SECRET_KEY, data_to_sign)
            
            return render(request, 'esewa.html',{
                'uid':uid,
                'amount': amount ,
                'tax_amount': tax_amount ,
                'total_amount': total_amount ,
                'product_code': settings.ESEWA_PRODUCT_CODE ,
                'signature' : result,
            }
            )

            
        elif pay_type == 'khalti':
            amount = cart_total_amount
            amount_in_paisa = amount * 100
            return render(request, 'khalti.html',{
                'uid':uuid.uuid4(),
                'amount': amount_in_paisa ,
            }
            )            
        if pay_type == 'custom_qr':
            # initiate_esewa(request)
            pass
    
    try:
        active_address= Address.objects.get(user=request.user,status=True)

    except:
        messages.warning(request,'Multiple address default, only one should be default')
    return render(request,'checkout_view.html',{
            "cart_data": request.session['cart_data_obj'],
            'total_cart_items':len(request.session['cart_data_obj']),
            'cart_total_amount':cart_total_amount,
            'active_address':active_address,
            })





def index(request):
    products = Product.objects.filter(product_status="published")
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    
    # Latest Products
    latest_products = Product.objects.filter(
        product_status="published", in_stock=True
    ).order_by('-mfd')[:6]
    
    # Top Rated Products
    top_rated_products = Product.objects.filter(
        product_status="published"
    ).annotate(
        average_rating=Avg('reviews__rating')  # Calculate the average rating from related reviews
    ).filter(
        average_rating__isnull=False  # Exclude products with no ratings
    ).order_by('-average_rating')[:3]
    
    # Reviewed Products (Products that have been reviewed)
    reviewed_products = Product.objects.filter(
        product_status="published"
    ).annotate(
        review_count=Count('reviews')  # Count the number of reviews for each product
    ).filter(
        review_count__gt=0  # Only include products with at least 1 review
    )[:6]  # Limit to 6 products, you can adjust this number

    context = {
        'products': products,
        'categories': categories,
        'vendors': vendors,
        'latest_products': latest_products,
        'top_rated_products': top_rated_products,
        'reviewed_products': reviewed_products,  # Add reviewed products to context
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
    user=request.user
    
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
        'user': user.username,
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

def add_to_cart(request):
    cart_product = {
        str(request.GET['id']): {
            'title': request.GET['title'],
            'price': float(request.GET['price']),  # Ensure price is a float for calculation
            'qty': int(request.GET['qty']),        # Ensure quantity is an integer
            'image': request.GET['image'],
            'pid': request.GET['pid'],
        }
    }

    if 'cart_data_object' in request.session:

        if str(request.GET['id']) in request.session['cart_data_object']:
            cart_data = request.session['cart_data_object']

            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_object'] = cart_data 
        else:
            cart_data = request.session['cart_data_object']
            cart_data.update(cart_product)
            request.session['cart_data_object'] = cart_data
    else:

        request.session['cart_data_object'] = cart_product


    

    return JsonResponse({
        "data": request.session['cart_data_object'],
        'totalcartitems': len(request.session['cart_data_object']),
        
    })

def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_object' in request.session:
        for product_id, item in request.session ['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, 'core/shoping-cart.html',{
            "cart_data": request.session['cart_data_object'],
            'total_cart_items':len(request.session['cart_data_object']),
            'cart_total_amount':cart_total_amount, # Total to be shown in the template
        })
    else:
        messages.error(request, 'Your cart is empty')
        return redirect('core:index')

def remove_from_cart(request):
    product_id = request.GET['id']
    
    if "cart_data_object" in request.session:
        if product_id in request.session["cart_data_object"]:
            cart_data = request.session["cart_data_object"]
            del request.session["cart_data_object"][product_id]
            request.session["cart_data_object"] = cart_data

    cart_total_amount = 0
    if 'cart_data_object' in request.session:
        for product_id, item in request.session['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = {
        'cart_data': request.session['cart_data_object'],
        'total_cart_items': len(request.session['cart_data_object']),
        'cart_total_amount': cart_total_amount,
    }

    
    cart_list_html = render_to_string('core/async/cart-list.html', context)

    return JsonResponse({
        'data': cart_list_html,
        "totalcartitems": len(request.session['cart_data_object']),
    })

def update_from_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']
    
    if "cart_data_object" in request.session:
        if product_id in request.session["cart_data_object"]:
            cart_data = request.session["cart_data_object"]
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session["cart_data_object"] = cart_data

    cart_total_amount = 0
    if 'cart_data_object' in request.session:
        for product_id, item in request.session['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = {
        'cart_data': request.session['cart_data_object'],
        'total_cart_items': len(request.session['cart_data_object']),
        'cart_total_amount': cart_total_amount,
    }

    
    cart_list_html = render_to_string('core/async/cart-list.html', context)

    return JsonResponse({
        'data': cart_list_html,
        "totalcartitems": len(request.session['cart_data_object']),
    })

def checkout(request):
    cart_total_amount = 0
    if 'cart_data_object' in request.session:
        for product_id, item in request.session['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        
    if request.method == 'POST':
        cart_total_amount=0
        if 'cart_data_object' in request.session:
         for product_id, item in request.session['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            order = CartOrder.objects.create(
                user = request.user,
                price= cart_total_amount

            )
            for product_id, item in request.session['cart_data_object'].items():
                cart_order_products = CartOrderItems.objects.create(
                    order = order,
                    invoice_no = "INVOICE_NO_"+str(order.id),
                    item=item['title'],
                    image=item['image'],
                    qty=item['qty'],
                    price=item['price'],
                    total=float(item['qty']) * float(item['price']),
                    


                )
        pay_type = request.POST.get('pay_type')
        if pay_type == 'esewa':
            uid = uuid.uuid4()
            tax_amount = 0 
            amount = cart_total_amount
            total_amount = amount + tax_amount
            data_to_sign = f"total_amount={total_amount},transaction_uuid={uid},product_code={settings.ESEWA_PRODUCT_CODE}"
            result= genSha256(settings.ESEWA_SECRET_KEY, data_to_sign)
            
            return render(request, 'core/esewa-request.html',{
                'uid':uid,
                'amount': amount ,
                'tax_amount': tax_amount ,
                'total_amount': total_amount ,
                'product_code': settings.ESEWA_PRODUCT_CODE ,
                'signature' : result,
            }
            )

            
        elif pay_type == 'khalti':
            amount = cart_total_amount
            amount_in_paisa = amount * 100
            return render(request, 'core/khalti.html',{
                'uid':uuid.uuid4(),
                'amount': amount_in_paisa ,
            }
            )            
        if pay_type == 'custom_qr':
            # initiate_esewa(request)
            pass
    
    try:
        active_address= Address.objects.get(user=request.user,status=True)

    except:
        messages.warning(request,'Multiple address default, only one should be default')
    return render(request,'core/checkout.html',{
            "cart_data": request.session['cart_data_object'],
            'total_cart_items':len(request.session['cart_data_object']),
            'cart_total_amount':cart_total_amount,
            'active_address':active_address,
            })


@login_required
def invoice(request):
    cart_total_amount = 0
    # Safely get cart_data_obj from the session
    cart_data = request.session.get('cart_data_object', {})

    # Calculate total amount if cart_data exists
    if cart_data:
        for product_id, item in request.session['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])  

    return render(request, 'core/invoice.html', {
        "cart_data": request.session['cart_data_object'],
            'total_cart_items':len(request.session['cart_data_object']),
            'cart_total_amount':cart_total_amount,
    })

    