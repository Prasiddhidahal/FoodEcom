from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauth.models import User
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import datetime
from django.contrib import admin

# Choices for Status fields
STATUS_CHOICES = [
    ('Active', 'Active'),
    ('outofstock', 'Out of Stock'),
    ('Pending', 'Pending'),
    ('Discontinued', 'Discontinued'),
    ('Inactive', 'Inactive'),
    
]
PRODUCT_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('disabled', 'Disabled'),
    ('rejected', 'Rejected'),
    ('published', 'Published'),
    ('archived', 'Archived'),
    ('Sale', 'Sale'),
]
ORDER_STATUS_CHOICES = [
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered')
]
RATING_CHOICES = [
    (1, '1 - Poor'),
    (2, '2 - Fair'),
    (3, '3 - Good'),
    (4, '4 - Very Good'),
    (5, '5 - Excellent')
]
METHOD=[
    ('COD','Cash On Delivery'),
    ('Esewa','Esewa'),
    ('Khalti','Khalti'),
]
ACTION_TYPES = (
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PRODUCT_CREATED', 'Product Created'),
        ('PRODUCT_UPDATED', 'Product Updated'),
        ('PRODUCT_DELETED', 'Product Deleted'),
        ('CATEGORY_CREATED', 'Category Created'),
        ('CATEGORY_UPDATED', 'Category Updated'),
        ('CATEGORY_DELETED', 'Category Deleted'),
    )

# Helper function to generate upload path
def user_directory_path(instance, filename):
    return 'user/{0}/{1}'.format(instance.title, filename)

class Navbar(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField(max_length=200, null=True, blank=True, default="http://127.0.0.1:8000/#")
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="Active")
    created_by = models.ForeignKey(User, related_name="created_navbars", on_delete=models.SET_NULL, null=True, blank=True)
    order = models.IntegerField(default=0)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

    class Meta:
        verbose_name_plural = "Navbar"
    
class Ad(models.Model):
    image = models.ImageField(upload_to="Ad")
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="Active")  # Increase max_length
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_Ad')

    class Meta:
        verbose_name_plural = "Ad"

    def ad_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)

    def __str__(self):
        return self.status


class Adimage(models.Model):
    ad = models.ForeignKey(Ad, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ad_images/')
    
    def ad_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)

    def __str__(self):
        return f"Image for {self.ad.status}"

    
class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdegh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category")
    
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="Active")  # Increase max_length
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_categories')

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)

    def __str__(self):
        return self.title


class CategoryImage(models.Model):
    category = models.ForeignKey(Category, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='category/images/')
    
    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)

    def __str__(self):
        return f"Image for {self.category.title}"

class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdegh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="vendors")
    description = RichTextUploadingField(null=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    shipping = models.CharField(max_length=100, default="Free Shipping")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="Active")  # Increase max_length
    price = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default="2.99")
    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)

    def __str__(self):
        return self.title

class Tags(models.Model):
    pass


class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdegh12345")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=100, default="Fresh Pear")
    image = models.ImageField(upload_to='products/') 
    description = RichTextUploadingField(null=True, blank=True, default="This is the product")
    price = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default="2.99")
    specifications = models.TextField(null=True, blank=True)
    tags=TaggableManager(blank=True)
    product_status = models.CharField(choices=PRODUCT_STATUS_CHOICES, max_length=10, default="draft")
    sku = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdegh12345")
    # Boolean Fields for Product Properties
    stock_quantity = models.PositiveIntegerField(default=0)  # You can set the default value as needed
    # Boolean Field to check if the product is available
    in_stock = models.BooleanField(default=True)
    in_sale = models.BooleanField(default=False) 
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')  # Rename to lowercase 'vendor'
    weight = models.FloatField(default=0)
    color = models.CharField(max_length=50, default="White")
    mfd=models.DateField(auto_now_add=True)
    life=models.IntegerField(default=30)
    shipping = models.CharField(max_length=100, default="Free Shipping")
    created_at = models.DateTimeField(default=datetime.now)
    sold_quantity = models.IntegerField(default=0)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_products')
    

    class Meta:
        verbose_name_plural = "Products"     

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)
    
    def stock_status(self):
        """Return a custom string based on stock quantity."""
        if self.stock_quantity > 0:
            return f"{self.stock_quantity} left"
        return "Out of stock"
    
    stock_status.short_description = 'Stock Status'

    def __str__(self):
        return self.title

    def get_percentage(self):
        return (self.price / self.old_price) * 100 if self.old_price else 0


#ProductImages#
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="products_images")
    image = models.ImageField(upload_to='products/images/')
    alt_text = models.CharField(max_length=100, default="Product Image")

    class Meta:
        verbose_name_plural = "Product Images"

#cartorder#
class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=30, default="processing")
    payment_method = models.CharField(choices=METHOD, max_length=30, default="COD")
    payment_completed = models.BooleanField(default=False)
    sold_quantity = models.IntegerField(default=0)
    in_stock = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Cart Orders"

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
    total = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
    invoice_no = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/" width="50" height="50" />' % self.image)




#Product Review#
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title if self.product else "Product Review"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return self.product.title if self.product else "Wishlist Item"
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField(max_length=200)
    mobile = models.TextField(max_length=10)
    status=models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.address}"


    




from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} performed {self.action_type} at {self.timestamp}"