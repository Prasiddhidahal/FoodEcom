from django.urls import path
from userauth import views

app_name = 'userauth'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),
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
    path('slider/', views.slider_list, name='slider_list'),
    path('slider/edit/<int:slider_id>/', views.slider_edit, name='slider_edit'),
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
    path('user_activity/', views.user_activity, name='user_activity'),
    path('ad/', views.ad_list, name='ad_list'),  # List all ads
    path('ad/edit/<int:ad_id>/', views.ad_edit, name='ad_edit'),  # Edit ad
    path('footers/', views.footers, name='footers'),
    path('footer/<int:footer_id>/', views.footer_view, name='footer_view'),
    path('footer/<int:footer_id>/edit/', views.footer_edit, name='footer_edit'),
    path('footer/<int:footer_id>/delete/', views.footer_delete, name='footer_delete'),
    path('about_company/', views.about_company, name='about_company'),
    path('about-company/edit/', views.about_company_edit, name='about_company_edit'),
]
