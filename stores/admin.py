from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    StoreCategory, ProductCategory, Store, StoreDelivery, DeliveryCompany,
    ProductAttribute, Product, ProductReview, ProductVariant, 
    ProductImage, Order, OrderItem, CustomerAddress, OrderShippingAddress, 
    Payment, OrderStatusHistory,
    Cart, CartItem
)

# --- 1. INLINES ---
# These allow you to edit related items on the same page
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ('attribute_values',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'price')

class StatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)

class CartItemInline(admin.StackedInline):
    model = CartItem
    extra = 0


class StoreDeliveryInline(admin.StackedInline):
    model = StoreDelivery
    extra = 0

# --- 2. ADMIN CLASSES ---

@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'name_fr', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'store_category')
    list_filter = ('store_category',)

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('subdomain', 'owner', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified', 'categories')
    search_fields = ('subdomain', 'name_en', 'owner__username')
    list_editable = ('is_active', 'is_verified',)
    fieldsets = (
        (_('Identity'), {'fields': ('owner', 'categories', 'subdomain', 'logo', 'banner')}),
        (_('Localization EN'), {'fields': ('name_en', 'tagline_en', 'description_en')}),
        (_('Localization AR'), {'fields': ('name_ar', 'tagline_ar', 'description_ar')}),
        (_('Localization FR'), {'fields': ('name_fr', 'tagline_fr', 'description_fr')}),
        (_('Social & Contact'), {'fields': ('watsapp_number', 'facebook_url', 'instagram_url', 'website_url')}),
        (_('Status'), {'fields': ('is_active', 'is_verified', 'is_featured')}),
    )
    inlines = [StoreDeliveryInline, ProductInline]

@admin.register(DeliveryCompany)
class DeliveryCompanyAdmin(admin.ModelAdmin):
    list_display = ('is_active',)

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('category', 'value_en', 'value_ar', 'color_code')
    list_filter = ('category',)
    search_fields = ('value_en', 'value_ar')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'store', 'base_price', 'is_active', 'is_new_arrival')
    list_filter = ('is_active', 'store', 'category')
    inlines = [ProductImageInline, ProductVariantInline, ProductReviewInline]
    fieldsets = (
        (_('General Info'), {'fields': ('store', 'category', 'main_image')}),
        (_('Names'), {'fields': ('name_en', 'name_ar', 'name_fr')}),
        (_('Pricing'), {'fields': ('base_price', 'discount')}),
        (_('Flags'), {'fields': ('is_active', 'is_featured', 'is_new_arrival', 'is_on_sale')}),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'store', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at', 'store')
    inlines = [OrderItemInline, StatusHistoryInline]
    readonly_fields = ('total_price', 'created_at', 'updated_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'status', 'created_at')
    list_filter = ('method', 'status')

@admin.register(OrderShippingAddress)
class OrderShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'wilaya', 'phone', 'order')

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'wilaya', 'phone', 'customer')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer',)
    inlines = [CartItemInline]

# Simple registration for remaining items
admin.site.register(ProductVariant)