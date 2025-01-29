from django.urls import path
from . import views

app_name = 'core'

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('shop-grid/', views.shop, name='shop'),  # Shop grid page
    # path('shop-details/', views.pages1, name='pages1'),  # Shop details page
    path('checkout/', views.checkout, name='checkout'),  # Checkout page
    path('contact/', views.contact, name='contact'),  # Contact page
    path('blog/', views.blog, name='blog'),  # Blog page
    path('blog-details/', views.blog_details, name='blog_details'),  # Blog details page
    path('categories/', views.categories, name='categories'),  # Categories page
    path('category/<str:cid>/', views.category_product_list, name='category_product_list'),  # Category product list with category id
    path('vendors/', views.vendor_list_view, name='vendor_list'),  # Vendor list page
    path('vendor_products/<str:vid>/', views.vendor_products, name='vendor_products'),
    path('shop-details/<str:pid>/', views.pages1, name='pages1'),
    path('products/tags/<slug:tag_slug>/', views.tag_list, name='tag_list'),
    path('add_review/<int:pid>/', views.add_review, name='add_review'),
    path('search/', views.search_products, name='search'),
    path('filter-product/', views.filter_product, name='filter-product'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('update_from_cart/', views.update_from_cart, name='update_from_cart'),
    path('khalti_verify/', views.khalti_verify,name='khalti_verify'),
    path('initiate_khalti/', views.initiate_khalti,name='initiate_khalti'),
    path('verify_esewa/', views.verify_esewa,name='verify_esewa'),
    path('invoice/', views.invoice,name='invoice'),
    path('customer_dashboard', views.customer_dashboard, name='customer_dashboard'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('make-default-address', views.make_default_address, name='make-default-address'),
   
]
    
    



