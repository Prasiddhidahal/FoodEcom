from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from core.models import CartOrder, CartOrderItems, Category, Product, ProductReview, Vendor, Wishlist, Address
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password1',  'bio']  

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'image']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'price', 'description', 'image', 'category', 'vendor', 'stock_quantity', 'product_status' ]  # Added category and vendor fields
    
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select Category")
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), empty_label="Select Vendor")
class OrderEditForm(forms.ModelForm):
    class Meta:
        model = CartOrder
        fields = [ 'price', 'product_status', 'payment_method', 'paid_status', 'payment_completed', 'in_stock']

class ProductEditForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'sku', 'price', 'old_price', 'stock_quantity', 
            'in_stock', 'category', 'vendor', 'weight', 'color', 
             'life', 'shipping', 'sold_quantity', 'description',
            'specifications', 'tags', 'image'
        ]


