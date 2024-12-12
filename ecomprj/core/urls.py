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
    path('shopping-cart/', views.cart, name='cart'),  # Shopping cart page
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
    path('add_review/<str:pid>/', views.add_review, name='add_review'),

  # Tags page
  # Product detail page with product id

]