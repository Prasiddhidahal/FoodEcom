from django.urls import path
from userauth import views

app_name = 'userauth'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('vendordashboard/', views.vendordashboard, name='vendordashboard'),
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

]
