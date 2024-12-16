from django.contrib import admin
from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, Wishlist, Address,Tags,  CategoryImage

# Inline model for displaying product images within the product admin view
class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

# Admin class for managing Product model in the admin interface
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'stock_status', 'in_stock', 'stock_quantity', 'vendor')
    list_filter = ('category', 'vendor')
    
    inlines = [ProductImagesAdmin]
# Admin class for managing Category model in the admin interface
class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 1  # Allow adding one extra image at a time

class CategoryAdmin(admin.ModelAdmin):
    inlines = [CategoryImageInline]
    list_display = ('cid', 'title', 'image')

# Admin class for managing Vendor model in the admin interface
class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor_image']

class TagsAdmin(admin.ModelAdmin):
    list_display = ['name']

# Admin class for managing CartOrder model in the admin interface
class CartOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status']

# Register the models with their respective admin classes

admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems)
admin.site.register(Wishlist)
admin.site.register(Address)
admin.site.register(Tags)
admin.site.register(ProductImages)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductReview)