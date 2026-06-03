from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from decimal import Decimal

# --- 1. GLOBAL INDUSTRY CATEGORIES ---
class StoreCategory(models.Model):
    """Industry level (e.g., Electronics, Fashion, Furniture)"""
    name_en = models.CharField(max_length=100, unique=True, verbose_name=_("Name (EN)"))
    name_ar = models.CharField(max_length=100, verbose_name=_("Name (AR)"))
    name_fr = models.CharField(max_length=100, verbose_name=_("Name (FR)"))
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True, verbose_name=_("Icon Image"))
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _("Store Category")
        verbose_name_plural = "Store Categories"

    @property
    def name(self):
        lang = translation.get_language()
        if lang == 'ar': return self.name_ar or self.name_en
        if lang == 'fr': return self.name_fr or self.name_en
        return self.name_en

    def __str__(self):
        return self.name_en

# --- 2. GLOBAL PRODUCT CATEGORIES (Linked to Industry) ---
class ProductCategory(models.Model):
    """Sub-categories (e.g., 'Smartphones' belongs to 'Electronics')"""
    store_category = models.ForeignKey(StoreCategory, on_delete=models.CASCADE, related_name='product_types')
    name_en = models.CharField(max_length=100, verbose_name=_("Name (EN)"))
    name_ar = models.CharField(max_length=100, verbose_name=_("Name (AR)"))
    name_fr = models.CharField(max_length=100, verbose_name=_("Name (FR)"))
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True, verbose_name=_("Icon Image"))

    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")

    @property
    def name(self):
        lang = translation.get_language()
        if lang == 'ar': return self.name_ar or self.name_en
        if lang == 'fr': return self.name_fr or self.name_en
        return self.name_en

    def __str__(self):
        return f"{self.store_category.name_en} > {self.name_en}"

# --- 3. THE STORE ---
class Store(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_store', verbose_name=_("Store Owner"))
    categories = models.ManyToManyField(StoreCategory, related_name='stores', verbose_name=_("Store Categories"))
    subdomain = models.SlugField(unique=True, verbose_name=_("Subdomain"))
    
    logo = models.ImageField(upload_to='stores/logos/', blank=True, null=True, verbose_name=_("Store Logo"))
    banner = models.ImageField(upload_to='stores/banners/', blank=True, null=True, verbose_name=_("Store Banner"))

    name_en = models.CharField(max_length=255, verbose_name=_("Store Name (EN)"))
    name_ar = models.CharField(max_length=255, verbose_name=_("Store Name (AR)"))
    name_fr = models.CharField(max_length=255, verbose_name=_("Store Name (FR)"))

    description_en = models.TextField(blank=True, null=True, verbose_name=_("Description (EN)"))
    description_ar = models.TextField(blank=True, null=True, verbose_name=_("Description (AR)"))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_("Description (FR)"))

    tagline_en = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Tagline (EN)"))
    tagline_ar = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Tagline (AR)"))
    tagline_fr = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Tagline (FR)"))

    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Is Featured"))

    watsapp_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("WhatsApp Number"))
    facebook_url = models.URLField(blank=True, null=True, verbose_name=_("Facebook URL"))
    instagram_url = models.URLField(blank=True, null=True, verbose_name=_("Instagram URL"))
    twitter_url = models.URLField(blank=True, null=True, verbose_name=_("Twitter URL"))
    linkedin_url = models.URLField(blank=True, null=True, verbose_name=_("LinkedIn URL"))
    website_url = models.URLField(blank=True, null=True, verbose_name=_("Website URL"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")

    @property
    def name(self):
        lang = translation.get_language()
        if lang == 'ar': return self.name_ar or self.name_en
        if lang == 'fr': return self.name_fr or self.name_en
        return self.name_en


    @property
    def tagline(self):
        lang = translation.get_language()
        if lang == 'ar': return self.tagline_ar or self.tagline_en
        if lang == 'fr': return self.tagline_fr or self.tagline_en
        return self.tagline_en


    @property
    def description(self):
        lang = translation.get_language()
        if lang == 'ar': return self.description_ar or self.description_en
        if lang == 'fr': return self.description_fr or self.description_en
        return self.description_en
    
    @property
    def products_count(self):
        return self.products.filter(is_active=True, variants__stock__gt=0).distinct().count()

    def __str__(self):
        return self.subdomain

# --- 4. ATTRIBUTE TYPES (Fixed List + Others) --
class ProductAttribute(models.Model):
    """
    A single model combining Attribute Types and their Values.
    Example: Category='COLOR', Value='Red', HEX='#FF0000'
    """
    class Category(models.TextChoices):
        COLOR = 'COLOR', _('Color')
        SIZE = 'SIZE', _('Size')
        MATERIAL = 'MATERIAL', _('Material')
        STORAGE = 'STORAGE', _('Storage')
        VOLTAGE = 'VOLTAGE', _('Voltage')
        OTHER = 'OTHER', _('Other')

    # 1. The Fixed Type
    category = models.CharField(
        max_length=20, 
        choices=Category.choices, 
        default=Category.OTHER,
        verbose_name=_("Attribute Category")
    )

    # 2. Custom Label (Used only if category is 'OTHER')
    # Example: if category is 'OTHER', label could be 'Weight' or 'Length'
    label_en = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Custom Label (EN)"))
    label_ar = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Custom Label (AR)"))
    label_fr = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Custom Label (FR)"))

    # 3. The Actual Value (The Choice)
    value_en = models.CharField(max_length=100, verbose_name=_("Value (EN)"))
    value_ar = models.CharField(max_length=100, verbose_name=_("Value (AR)"))
    value_fr = models.CharField(max_length=100, verbose_name=_("Value (FR)"))

    # 4. Extra Data (Specific to Colors)
    color_code = models.CharField(
        max_length=7, 
        blank=True, 
        null=True, 
        help_text=_("HEX Code e.g. #000000 (Only for Colors)"), verbose_name=_("Color HEX Code")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")

    @property
    def display_label(self):
        """Returns the category name or the custom label based on active language"""
        lang = translation.get_language()
        if self.category == self.Category.OTHER:
            if lang == 'ar': return self.label_ar or self.label_en
            if lang == 'fr': return self.label_fr or self.label_en
            return self.label_en
        return self.get_category_display()

    @property
    def value(self):
        """Returns the value based on active language"""
        lang = translation.get_language()
        if lang == 'ar': return self.value_ar or self.value_en
        if lang == 'fr': return self.value_fr or self.value_en
        return self.value_en

    def __str__(self):
        return f"{self.get_category_display()}: {self.value_en}"
    
# --- 5. THE PRODUCT ---
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', verbose_name=_("Store"))
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, verbose_name=_("Product Category"))

    name_en = models.CharField(max_length=255, verbose_name=_("Product Name (EN)"))
    name_ar = models.CharField(max_length=255, verbose_name=_("Product Name (AR)"))
    name_fr = models.CharField(max_length=255, verbose_name=_("Product Name (FR)"))

    description_en = models.TextField(blank=True, null=True, verbose_name=_("Product Description (EN)"))
    description_ar = models.TextField(blank=True, null=True, verbose_name=_("Product Description (AR)"))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_("Product Description (FR)"))
    
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Base Price"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_("Discount %"))
    main_image = models.ImageField(upload_to='products/main/', verbose_name=_("Main Image"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Is Featured"))
    is_new_arrival = models.BooleanField(default=False, verbose_name=_("Is New Arrival"))
    is_on_sale = models.BooleanField(default=False, verbose_name=_("Is On Sale"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    @property
    def discounted_price(self):
        if self.discount:
            return self.base_price * (Decimal("1") - (self.discount / Decimal("100")))
        return self.base_price
    @property
    def name(self):
        lang = translation.get_language()
        if lang == 'ar': return self.name_ar or self.name_en
        if lang == 'fr': return self.name_fr or self.name_en
        return self.name_en
    
    @property
    def description(self):
        lang = translation.get_language()
        if lang == 'ar': return self.description_ar or self.description_en
        if lang == 'fr': return self.description_fr or self.description_en
        return self.description_en
    
    @property
    def stock(self):
        """Calculate total stock across all variants"""
        return sum(variant.stock for variant in self.variants.all())

    def get_summary_attributes(self):
        """Returns a unique list of non-color attributes (e.g., Size, Material)."""
        return ProductAttribute.objects.filter(
            variant_combos__product=self
        ).exclude(category='COLOR').distinct()[:3] # Limit to 3 to keep the card clean
    
    def get_unique_colors(self):
        """Returns a unique list of color attributes associated with this product's variants."""
        # We look through all variants, find their attribute values where category is COLOR,
        # and use .distinct() to remove duplicates.
        from .models import ProductAttribute # Local import to avoid circular dependency
        return ProductAttribute.objects.filter(
            variant_combos__product=self,
            category='COLOR'
        ).distinct()

    def get_unique_colors_with_stock(self):
        colors_dict = {}
        # Iterate over prefetched variants to sum stock per color attribute
        for variant in self.variants.all():
            for attr in variant.attribute_values.all():
                if attr.category == 'COLOR':
                    if attr.id not in colors_dict:
                        # Copy the attr to avoid modifying the original cached object
                        colors_dict[attr.id] = attr
                        colors_dict[attr.id].total_stock = 0
                    colors_dict[attr.id].total_stock += variant.stock
        return colors_dict.values()

    def get_grouped_card_attributes_with_stock(self):
        from collections import defaultdict
        grouped = defaultdict(dict)
        
        for variant in self.variants.all():
            for attr in variant.attribute_values.all():
                if attr.category != 'COLOR':
                    cat_key = attr.category
                    if attr.id not in grouped[cat_key]:
                        # Using a dict inside defaultdict to keep attributes unique per category
                        attr.total_stock = 0
                        grouped[cat_key][attr.id] = attr
                    grouped[cat_key][attr.id].total_stock += variant.stock
        
        # Convert to a format template can easily loop: { 'SIZE': [attr1, attr2], ... }
        final_grouped = {
            label: list(attrs.values()) 
            for label, attrs in grouped.items()
        }
        return final_grouped
    
    @property
    def status_badge(self):
        """
        Evaluates boolean flags to return styling configuration and text 
        for the front-end card overlay badges.
        """
        if self.is_on_sale and self.discount:
            return {
                'label': _("Sale"),
                'class': "bg-red-500 text-white shadow-red-500/20"
            }
        elif self.is_new_arrival:
            return {
                'label': _("New"),
                'class': "bg-teal-500 text-white shadow-teal-500/20"
            }
        elif self.is_featured:
            return {
                'label': _("Featured"),
                'class': "bg-amber-500 text-white shadow-amber-500/20"
            }
        return None
    
    def __str__(self):
        return self.name_en

# --- 6. THE VARIANT (The Specific Combo) ---
class ProductVariant(models.Model):
    """Specific combination: e.g., T-Shirt Red XL"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name=_("Base Product"))
    # Use ManyToMany to combine multiple attributes (Size + Color)
    attribute_values = models.ManyToManyField(ProductAttribute, related_name='variant_combos', verbose_name=_("Attribute Values"))

    price_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_("Price Override"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name=_("SKU"))

    class Meta:
        verbose_name = _("Product Variant")
        verbose_name_plural = _("Product Variants")


    def __str__(self):
        vals = " / ".join([v.value_en for v in self.attribute_values.all()])
        return f"{self.product.name_en} ({vals})"
    
# --- 7. PRODUCT IMAGES (Multiple Images per Product) ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_("Product"))
    image = models.ImageField(upload_to='products/gallery/', verbose_name=_("Image"))
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Alt Text"))

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def __str__(self):
        return f"Image for {self.product.name}"

# --- 8. PRODUCT REVIEWS ---
class ProductReview(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("Product"))
    customer=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Customer"))
    rating=models.PositiveSmallIntegerField(default=5, verbose_name=_("Rating"), help_text=_("Rating from 1 to 5"))
    comment=models.TextField(blank=True, null=True, verbose_name=_("Comment"))
    created_at=models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Product Review")
        verbose_name_plural = _("Product Reviews")
        ordering=["-created_at"]

# --- 8. THE ORDER ---
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        PROCESSING = 'PROCESSING', _('Processing')
        SHIPPED = 'SHIPPED', _('Shipped')
        DELIVERED = 'DELIVERED', _('Delivered')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REFUNDED = 'REFUNDED', _('Refunded')

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name=_("Customer"))
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', verbose_name=_("Store"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_("Order Status"))
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Total Price"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"
    
# --- 9. ORDER ITEMS (Products within an Order) ---
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("Order"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ordered_items', verbose_name=_("Product"))
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Product Variant"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=10,decimal_places=2, verbose_name=_("Price at purchase time"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        return f"{self.product.name_en} x {self.quantity}"


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')

    full_name = models.CharField(max_length=255, verbose_name=_("Full Name"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))

    address = models.CharField(max_length=255, verbose_name=_("Address"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("State"))
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Postal Code"))
    country = models.CharField(max_length=100, default="Algeria", verbose_name=_("Country"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")

    def __str__(self):
        return f"{self.full_name} - {self.city}"

class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'CASH', _('Cash on Delivery')
        CARD = 'CARD', _('Card')
        CCP = 'CCP', _('CCP')
        BARIDI = 'BARIDI', _('BaridiMob')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PAID = 'PAID', _('Paid')
        FAILED = 'FAILED', _('Failed')

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name=_("Order"))
    method = models.CharField(max_length=20, choices=Method.choices, verbose_name=_("Payment Method"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_("Payment Status"))
    transaction_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Transaction ID"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self):
        return f"Payment for Order #{self.order.id}"
    
class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history', verbose_name=_("Order"))
    status = models.CharField(max_length=20, choices=Order.Status.choices, verbose_name=_("Order Status"))
    note = models.TextField(blank=True, null=True, verbose_name=_("Note"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Order Status History")
        verbose_name_plural = _("Order Status Histories")

    def __str__(self):
        return f"{self.order.id} - {self.status}"