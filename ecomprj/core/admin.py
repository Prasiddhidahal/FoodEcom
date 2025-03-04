from django.contrib import admin
from core.models import About_company, Ad, Adimage, Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, Wishlist, Address,Tags,  CategoryImage, Navbar, Slider, Footer, About_company


@admin.register(Navbar)
class NavbarAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'status')  # Display these fields in the list view
    list_filter = ('status',)  # Add a filter for status
    search_fields = ('title', 'url')  # Add search functionality for title and url
    ordering = ('order',)  # Optionally, add ordering by title

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'status', 'order', 'parent', 'created_by', 'logo')
    list_filter = ('status', 'parent', 'created_by')
    search_fields = ('title', 'url', 'status', 'order', 'parent', 'created_by', 'logo')

@admin.register(About_company)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'updated_by')
    search_fields = ('title', 'description',  'updated_by')
class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class AdImageInline(admin.TabularInline):
    model = Adimage
    extra = 1  # Number of empty forms to display initially

# ModelAdmin for Ad
class AdAdmin(admin.ModelAdmin):
    list_display = ('image', 'status')
    list_filter = ('status',)
    search_fields = ('image', 'status')
    inlines = [AdImageInline]  

# Register the Ad model with the admin site
admin.site.register(Ad, AdAdmin)

class sliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'slider_image', 'status', 'updated_by')
    list_filter = ('status',)
    search_fields = ('title', 'status')
    readonly_fields = ('slider_image',)  # Show the image in the admin

admin.site.register(Slider, sliderAdmin)
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

class AddressesAdmin(admin.ModelAdmin):
    list_editable = ['address', 'status']
    list_display = ['user', 'address', 'status']
# @admin.register(ActivityLog)


# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ('user', 'message', 'is_read', 'timestamp')
#     list_filter = ('is_read', 'timestamp')
#     search_fields = ('user__username', 'message')

#     class Meta:
#         model = Notification
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



# admin.site.register(ActivityLog)