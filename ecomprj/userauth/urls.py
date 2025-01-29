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
    path('navbars/', views.navbars, name='navbars'),
    path('navbars/<int:navbar_id>/', views.navbar_view, name='navbar_view'),
    path('navbars/<int:navbar_id>/edit/', views.navbar_edit, name='navbar_edit'),
    path('navbars/<int:navbar_id>/delete/', views.navbar_delete, name='navbar_delete'),
    
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product_view, name='product_view'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),
     path('category/delete/<int:id>/', views.category_delete, name='category_delete'),
     path('category/edit/<int:id>/', views.category_edit, name='category_edit'),
    path('manage_roles/', views.manage_roles, name='manage_roles'),
     path('manage_group_permissions', views.manage_group_permissions, name='manage_group_permissions'),
     path('activity-log/', views.activity_log_view, name='activity_log'),
    #  path('notification_list/', views.notification_list, name='notification_list'),
    # path('mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    # path('delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('user_activity/', views.user_activity, name='user_activity'),
    path('ad/', views.ad_list, name='ad_list'),  # List all ads
    path('ad/edit/<int:ad_id>/', views.ad_edit, name='ad_edit'),  # Edit ad
    path('ad/delete/<int:ad_id>/', views.ad_delete, name='ad_delete'),  # Delete ad

]
