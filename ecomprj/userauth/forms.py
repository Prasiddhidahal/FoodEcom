from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from core.models import  About_company, CartOrder, CartOrderItems, Category, Product, ProductReview, Vendor, Wishlist, Address
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group, Permission


User = get_user_model()
from core.models import Navbar, Footer

class NavbarForm(forms.ModelForm):
    class Meta:
        model = Navbar
        fields = ['title', 'url', 'status', 'order', 'parent', 'created_by']

class FooterForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = ['title', 'url', 'status', 'order', 'parent', 'created_by', 'logo']


from core.models import Ad, Adimage

# Form for the Ad model
class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['status', 'image']
    
    # Override the image field to make it optional during edit
    image = forms.ImageField(required=False)

# Form for the Adimage model (single image)
class AdImageForm(forms.ModelForm):
    class Meta:
        model = Adimage
        fields = ['image'] 
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password1',  'bio']  

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'image']

from django import forms
from core.models import Slider

class SliderForm(forms.ModelForm):
    class Meta:
        model = Slider
        fields = ['title',  'image', 'description', 'updated_by', 'status']  

class About_companyForm(forms.ModelForm):
    class Meta:
        model = About_company
        fields = ['title', 'description', 'image', 'updated_by']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'price', 'description', 'image', 'category', 'vendor', 'stock_quantity', 'product_status',]
    
    # in_sale = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))
    # updated_by = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput(), required=False)
  # Added category and vendor fields
    
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
            'specifications', 'tags', 'image', 'in_sale',
        ]
# updated_by = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput(), required=False)
class AssignRoleForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User", required=True)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Assign Role", required=False)  # Existing roles
    # new_group = forms.CharField(max_length=100, label="Create New Role", required=False)  # Field for new role creation

    def clean(self):
        cleaned_data = super().clean()
        # new_group_name = cleaned_data.get('new_group')
        group = cleaned_data.get('group')

        # If a new group is provided, make sure no existing group is selected
        # if new_group_name and group:
        #     raise forms.ValidationError("Please choose either an existing group or create a new one, not both.")

        return cleaned_data

# class CreateGroupForm(forms.ModelForm):
#     class Meta:
#         model = Group
#         fields = ['name']
#         labels = {'name': 'Role Name'}

#     def clean_name(self):
#         name = self.cleaned_data.get('name')
#         if Group.objects.filter(name=name).exists():
#             raise forms.ValidationError(f"Group with name '{name}' already exists.")
#         return name
class CreateRoleForm(forms.Form):
    role_name = forms.CharField(max_length=100, label="Role Name")
    
    def clean_role_name(self):
        role_name = self.cleaned_data.get('role_name')
        if Group.objects.filter(name=role_name).exists():
            raise forms.ValidationError(f"Group with name '{role_name}' already exists.")
        return role_name
    
class GroupPermissionForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(),

        widget=forms.CheckboxSelectMultiple,
        label="Assign Permissions"
    )