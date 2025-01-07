from django.urls import path
from userauth import views

app_name = 'userauth'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),
    path('vendormanagement/', views.vendor_management, name='vendormanagement'),
    path('delete_vendor/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),
    path('edit_vendor/<int:vendor_id>/', views.edit_vendor, name='edit_vendor'),
    # path('view_user/<int:id>/', views.view_user, name='view_user'),  # Assuming view_user is a separate function
    # path('view_post/<int:post_id>/', views.view_post, name='view_post'),  # Assuming view_post is a separate function
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    # path('authorinfo/', views.vendorinfo, name='authorinfo'),
    # path('settings/', views.settings, name='settings'),  # Assuming settings is a separate function
    path('unauthorized/', views.unauthorized, name='unauthorized'),
    path('products/', views.products, name='products'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_view, name='order_view'),
    path('orders/<int:order_id>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:order_id>/delete/', views.order_delete, name='order_delete'),
    path('customers/', views.customer_orders, name='customer_orders'),
    path('customer/<int:user_id>/orders/', views.customer_order_details, name='customer_order_details'),  # Added URL for details
    path('add_product/', views.add_product, name='add_product'),
    
    
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product_view, name='product_view'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),

    

]
