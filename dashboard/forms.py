from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from accounts.models import User, UserProfile
from stores.management.commands.seed_data import User
from stores.models import StoreCategory, ProductCategory, Store, Product, ProductImage, ProductAttribute, ProductVariant
from studio.models import Project, ProjectImage, ProjectImage, Service, Package, PackageFeature, Testimonial, ContactMessage

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = "__all__"

ProjectImageFormSet = inlineformset_factory(Project, ProjectImage, form=ProjectImageForm, extra=0, can_delete=True)


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = "__all__"


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = "__all__"


class PackageFeatureForm(forms.ModelForm):
    class Meta:
        model = PackageFeature
        fields = "__all__"

PackageFeatureFormSet = inlineformset_factory(Package, PackageFeature, form=PackageFeatureForm, extra=0, can_delete=True)


# =========================================================
# STORES & PRODUCTS
# =========================================================

class StoreCategoryForm(forms.ModelForm):
    class Meta:
        model = StoreCategory
        fields = ['name_en', 'name_ar', 'name_fr', 'icon', 'slug']
        widgets = {
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('English Name')}),
            'name_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Arabic Name')}),
            'name_fr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('French Name')}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Slug')}),
            'icon': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name_en', 'name_ar', 'name_fr', 'icon']
        widgets = {
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('English Name')}),
            'name_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Arabic Name')}),
            'name_fr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('French Name')}),
            'icon': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

ProductCategoryFormSet = inlineformset_factory(
    StoreCategory, 
    ProductCategory,
    form=ProductCategoryForm,
    extra=0,
    can_delete=True
)


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'owner', 'subdomain', 
            'name_en', 'name_ar', 'name_fr', 'description_en', 'description_ar', 'description_fr', 
            'tagline_en', 'tagline_ar', 'tagline_fr', 'logo', 'banner', 
            'watsapp_number', 'facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'website_url', 
            'is_verified', 'is_active', 'is_featured', 'categories'
        ]

        widgets = {
            'owner': forms.Select(attrs={'class': 'form-control'}),
            'subdomain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Subdomain')}),
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Store Name (EN)')}),
            'name_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Store Name (AR)')}),
            'name_fr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Store Name (FR)')}),
            'description_en': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Store Description (EN)')}),
            'description_ar': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Store Description (AR)')}),
            'description_fr': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Store Description (FR)')}),
            'tagline_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Tagline (EN)')}),
            'tagline_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Tagline (AR)')}),
            'tagline_fr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Tagline (FR)')}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'banner': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'watsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('WhatsApp Number')}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Facebook URL')}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Instagram URL')}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Twitter URL')}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('LinkedIn URL')}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Website URL')}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'store', 'category', 'name_en', 'name_ar', 'name_fr', 
            'description_en', 'description_ar', 'description_fr', 
            'base_price', 'discount', 'main_image', 
            'is_active', 'is_featured', 'is_new_arrival', 'is_on_sale'
        ]

        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Product Name (EN)')}),
            'name_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Product Name (AR)')}),
            'name_fr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Product Name (FR)')}),
            'description_en': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Product Description (EN)')}),
            'description_ar': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Product Description (AR)')}),
            'description_fr': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Product Description (FR)')}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Base Price')}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Discount %')}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new_arrival': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_on_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        
        fields = ['price_override', 'stock', 'sku', 'attribute_values']
        widgets = {
            'price_override': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Price Override')}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Stock Quantity')}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('SKU')}),
            'attribute_values': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Alt Text')}),
        }

class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute

        fields = [
            'category',
            'label_en', 'label_ar', 'label_fr',
            'value_en', 'value_ar', 'value_fr',
            'color_code',
        ]

        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'label_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Label (EN)')}),
            'label_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Label (AR)')}),
            'label_fr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Label (FR)')}),
            'value_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Value (EN)')}),
            'value_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Value (AR)')}),
            'value_fr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Value (FR)')}),
            'color_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Color Code (Hex)')}),
        }


ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True
)

ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=1,
    can_delete=True
)

# =========================================================
# ACCOUNTS
# =========================================================
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "first_name_ar", "last_name_ar", "email", "phone", "role", "groups","is_active", "is_staff", "is_superuser")

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username')}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('First Name')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Last Name')}),
            'first_name_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('First Name (AR)')}),
            'last_name_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Last Name (AR)')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Phone')}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-control'}),
            # 'permissions': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("avatar", "bio_ar", "bio_en", "bio_fr", "company_name", "wilaya", "address", "is_verified")

        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'bio_ar': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Bio (AR)')}),
            'bio_en': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Bio (EN)')}),
            'bio_fr': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Bio (FR)')}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Company Name')}),
            'wilaya': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Address')}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
