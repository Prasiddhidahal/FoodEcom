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
import calendar
from datetime import datetime
from django.db.models.functions import ExtractMonth
from .models import  About_company, Footer, Navbar, Category, Ad, Slider 

# Function to generate HMAC SHA256 signature
def genSha256(key, message):
    key = key.encode('utf-8')
    message = message.encode('utf-8')

    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode('utf-8')

    return signature
#modes of payment 
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
        }
    })
    headers = {
        'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.text:
        try:
            new_res = response.json()  
        except ValueError as e:
            print("Error parsing JSON:", e)
            
    else:
        print("Empty response:", response.text)
    
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
    
    if new_res['status'] == 'Completed':
        messages.success(request,"Payment completed successfully.")
        return redirect('core:invoice')  
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
               return redirect('core:invoice')  # Redirect to the invoice page

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


def index(request):
    products = Product.objects.filter(product_status="published")
    categories = Category.objects.all()
    vendors = Vendor.objects.all()

    latest_products = Product.objects.filter(
        product_status="published", in_stock=True
    ).order_by('-mfd')[:6]
    
    in_sale = Product.objects.filter(in_sale=True, product_status="published")[:6]
    top_rated_products = Product.objects.filter(
        product_status="published"
    ).annotate(
        average_rating=Avg('reviews__rating')  
    ).filter(
        average_rating__isnull=False 
    ).order_by('-average_rating')[:3]
    reviewed_products = Product.objects.filter(
        product_status="published"
    ).annotate(
        review_count=Count('reviews')
    ).filter(
        review_count__gt=0
    )[:6]  
    navbars = Navbar.objects.filter(status='Active').order_by('order')
    ads = Ad.objects.filter(status='Active').prefetch_related('images')[:1]
    ads2 = Ad.objects.filter(status='Active').prefetch_related('images')[1:]
    slider = Slider.objects.filter(status='Active').order_by('status')
    footer=Footer.objects.filter()
    

    context = {
        'products': products,
        'categories': categories,
        'vendors': vendors,
        'latest_products': latest_products,
        'top_rated_products': top_rated_products,
        'reviewed_products': reviewed_products,
        'in_sale': in_sale,
        'navbars': navbars, 
        'ads': ads  ,
        'ads2': ads2,
        'slider': slider,
        'footer':footer, 
        
    }

    return render(request, 'core/index.html', context)

#category
def categories(request):
    products=Product.objects.filter(product_status="published")
    categories = Category.objects.all()
    for category in categories:
        category.product_count = Product.objects.filter(category=category).count()
    navbars = Navbar.objects.filter(status='Active').order_by('order')
    footer=Footer.objects.filter()
    context = {
        'categories': categories,
        'products':products,
        'navbars': navbars,
        'footer':footer,
    }

    return render(request, 'core/category_products.html', context)

def category_product_list(request, cid):
    category = Category.objects.get ( cid=cid) 
    products = Product.objects.filter(product_status="published", category=category)
    navbars = Navbar.objects.filter(status='Active').order_by('order')
    footer=Footer.objects.filter()
    context = {
        'category': category,
        'products': products,
        'navbars': navbars,
        'footer':footer,

    }

    return render(request, 'core/category_product_list.html', context)

def contact(request):
    categories = Category.objects.all()
    navbars = Navbar.objects.filter(status='Active').order_by('order')
    footer=Footer.objects.filter()
    context = {
        'categories': categories,
        'navbars': navbars,
        'footer':footer,
    }
    return render(request, 'core/contact.html', context)

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
    vendor = get_object_or_404(Vendor, vid=vid) 
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
    vendors = Vendor.objects.all()  
    tags = Tag.objects.all()   
    navbars = Navbar.objects.filter(status='Active').order_by('order')
    footer=Footer.objects.filter()
    tag_slug = request.GET.get('tag') 

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug) 
        latest_products = latest_products.filter(tags__in=[tag])  

    context = {
        'categories': categories,
        'latest_products': latest_products,
        'vendors': vendors,  
        'tags': tags,  
        'selected_tag': tag_slug,
        'navbars': navbars,
        'footer':footer,
    }
    return render(request, 'core/shop-grid.html', context)

#product page
def pages1(request, pid):
    product = get_object_or_404(Product, id=pid)
    related_products = Product.objects.filter(
        category=product.category,
        product_status="published"
    ).exclude(id=pid)[:4] 
    products_images = product.products_images.all()
    address = None
    if request.user.is_authenticated:
        address = Address.objects.filter(user=request.user).first()

    reviews=ProductReview.objects.filter(
        product=product
    ).order_by("-date")
    star_range = list(range(1, 6))
    # get 5 average rating
     # Get the count of reviews for each rating (1 to 5 stars)
    ratings = (
        ProductReview.objects.filter(product=product)
        .values('rating')
        .annotate(count=Count('rating'))
    )
    product = get_object_or_404(
        Product.objects.prefetch_related("color", "size"), 
        id=pid
    )
    # Create a dictionary with default values (0) for each star rating
    ratings_dict = {star: 0 for star in star_range}

    # Populate the dictionary with actual counts from the query
    for item in ratings:
        ratings_dict[item['rating']] = item['count']
    # Getting average review
    average_review = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    total_reviews = sum(ratings_dict.values())
    ratings_percentage = {star: (ratings_dict[star] / total_reviews * 100) if total_reviews > 0 else 0.0
                          for star in star_range}
    make_review=True
    if request.user.is_authenticated:
            user_review_count = ProductReview.objects.filter(user=request.user,product=product).count()
            if user_review_count > 0:
                make_review=False
    navbars = Navbar.objects.filter(status='Active').order_by('order')
    footer=Footer.objects.filter()
    
    
    # Add this line to access size choices
    size = Product.size
    color= Product.color
    context = {
        'review_form': ProductReviewForm(),
        'product': product,
        'related_products': related_products,
        'products_images': products_images,
        "reviews":reviews,
        "average_review":average_review,
        "star_range":star_range,
        "ratings":ratings_dict,
        "ratings_percentage":ratings_percentage,
        "make_review":make_review,  
        'address': address,
        'navbars': navbars,
        'footer':footer,
        'size': size,
        'color':color,
    }

    return render(request, 'core/pages1.html', context)

def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")
    tag = None
    navbars = Navbar.objects.filter(status='Active').order_by('order')
    footer=Footer.objects.filter()
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)  
        products = products.filter(tags__in=[tag])  

    context = {
        'products': products,
        'tag': tag,
        'navbars': navbars,
        'footer':footer,
    }
    return render(request, 'core/tag.html', context)

def add_review(request, pid):
    product = get_object_or_404(Product, id=pid)
    user=request.user
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ProductReviewForm(request.POST)
        
        if form.is_valid():
            if ProductReview.objects.filter(product=product, user=request.user).exists():
                return JsonResponse({'bool': False, 'message': 'You have already reviewed this product'}, status=400)
            
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
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
    products = Product.objects.filter(title__icontains=query)
    navbars = Navbar.objects.filter(status='Active').order_by('order')
    footer=Footer.objects.filter()
    context = {
        'products': products,
        'query': query,
        'navbars': navbars,
        'footer':footer,
    }
    return render(request, 'core/search.html', context)

def filter_product(request):
    category_slugs = request.GET.getlist('category[]')  
    vendor_ids = request.GET.getlist('vendor[]') 
    tag_ids = request.GET.getlist('tag[]') 
    min_price = request.GET.get('min_price', 0) 
    max_price = request.GET.get('max_price', 1000000)  

    try:
        min_price = float(min_price)
        max_price = float(max_price)
    except ValueError:
        min_price = 0
        max_price = 1000000

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()
    products = products.filter(price__gte=min_price, price__lte=max_price)

    if category_slugs:
        products = products.filter(category__slug__in=category_slugs).distinct()

    if vendor_ids:
        products = products.filter(vendor__id__in=vendor_ids).distinct()

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
    category_cids = request.GET.getlist('category[]') 
    vendor_vids = request.GET.getlist('vendor[]')  
    tag_slugs = request.GET.getlist('tag[]')
    
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)

    if min_price is not None:
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = None  

    if max_price is not None:
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = None  

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()

    if min_price is not None and max_price is not None:
        products = products.filter(price__gte=min_price, price__lte=max_price)
    elif min_price is not None:
        products = products.filter(price__gte=min_price)
    elif max_price is not None:
        products = products.filter(price__lte=max_price)

    if category_cids:
        products = products.filter(category__cid__in=category_cids).distinct()

    if vendor_vids:
        products = products.filter(vendor__vid__in=vendor_vids).distinct()

    if tag_slugs:
        products = products.filter(tags__slug__in=tag_slugs).distinct()

    tags = Tag.objects.all()

    context = {
        "products": products,
        "tags": tags, 
    }
    data = render_to_string("core/async/product-list.html", context)

    return JsonResponse({
        "data": data,
    })

def add_to_cart(request):
    color = request.GET.get('color', 'Default Color')
    size = request.GET.get('size', 'Default Size')

    # Convert price and quantity to appropriate types
    price = float(request.GET.get('price', 0))
    qty = int(request.GET.get('qty', 1))

    cart_product = {
        str(request.GET['id']): {
            'title': request.GET.get('title', ''),
            'price': price,
            'qty': qty,
            'image': request.GET.get('image', ''),
            'pid': request.GET.get('pid', ''),
            'color': color,
            'size': size,
        }
    }

    # Check if 'cart_data_object' exists in the session
    if 'cart_data_object' in request.session:
        cart_data = request.session['cart_data_object']

        # Update existing product in the cart
        if str(request.GET['id']) in cart_data:
            # Convert existing qty to integer before adding
            cart_data[str(request.GET['id'])]['qty'] = int(cart_data[str(request.GET['id'])]['qty']) + qty
            cart_data[str(request.GET['id'])]['color'] = color  # Ensure color is updated
            cart_data[str(request.GET['id'])]['size'] = size  # Ensure size is updated
            request.session['cart_data_object'] = cart_data
        else:
            # Add new product to the cart
            cart_data.update(cart_product)
            request.session['cart_data_object'] = cart_data
    else:
        # Create a new cart and add the product
        request.session['cart_data_object'] = cart_product

    # Debug: Print session data to the console to verify
    print("Cart Data in Session:", request.session['cart_data_object'])

    return JsonResponse({
        "data": request.session['cart_data_object'],
        'totalcartitems': len(request.session['cart_data_object']),
    })


def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_object' in request.session:
        for product_id, item in request.session['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        
        return render(request, 'core/shoping-cart.html', {
            "cart_data": request.session['cart_data_object'],
            'total_cart_items': len(request.session['cart_data_object']),
            'cart_total_amount': cart_total_amount,
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
    cart_data = request.session.get('cart_data_object', {})  


    if cart_data:
        for product_id, item in cart_data.items():
            cart_total_amount += int(item['qty']) * float(item['price'])


    if request.method == 'POST':
        cart_total_amount = 0
        for product_id, item in cart_data.items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            order = CartOrder.objects.create(
                user=request.user,
                price=cart_total_amount

            )
            for product_id, item in cart_data.items():
                CartOrderItems.objects.create(
                    order=order,
                    invoice_no="INVOICE_NO_" + str(order.id),
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
            result = genSha256(settings.ESEWA_SECRET_KEY, data_to_sign)

            return render(request, 'core/esewa-request.html', {
                'uid': uid,
                'amount': amount,
                'tax_amount': tax_amount,
                'total_amount': total_amount,
                'product_code': settings.ESEWA_PRODUCT_CODE,
                'signature': result,
            })

        elif pay_type == 'khalti':
            amount = cart_total_amount
            amount_in_paisa = amount * 100
            return render(request, 'core/khalti.html', {
                'uid': uuid.uuid4(),
                'amount': amount_in_paisa,
            })

    return render(request, 'core/checkout.html', {
        'cart_data': cart_data,
        'total_cart_items': len(cart_data),
        'cart_total_amount': cart_total_amount,
    })

@login_required
def invoice(request):
    cart_total_amount = 0
    cart_data = request.session.get('cart_data_object', {})

    if cart_data:
        for product_id, item in cart_data.items():
            cart_total_amount += int(item['qty']) * float(item['price'])  

    return render(request, "core/invoice.html", {
        'cart_data': cart_data,
        'total_cart_items': len(cart_data),
        'cart_total_amount': cart_total_amount,
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id, user=request.user)
    order_items = CartOrderItems.objects.filter(order=order)
    order_date = order.order_date
    
    context = {
        'order': order,
        'order_items': order_items,
        'order_date': order_date
    }
    return render(request, 'core/order_detail.html', context)
    
@login_required
def customer_dashboard(request):
    orders_list=CartOrder.objects.filter(user=request.user).order_by('-id')
    address= Address.objects.filter(user=request.user)
    orders= CartOrder.objects.annotate(month= ExtractMonth('order_date')).values('month').annotate(count=Count('id')).values('month', 'count')
    if request.method == 'POST':
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
            status=True
        )
        messages.success(request, 'Address added successfully')
        return redirect('core:customer_dashboard')
    context={
        'orders': orders,
        'orders_list':orders_list,
        'address':address
    }
    return render(request, 'core/customer_dashboard.html', context)

def make_default_address(request):
    id = request.GET.get('id')
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({'boolean': True})

def about_company(request):
    about_company = get_object_or_404(About_company, id=1)  # Fetch the 'About Company' content
    return render(request, 'core/about_company.html', {'about_company': about_company})
