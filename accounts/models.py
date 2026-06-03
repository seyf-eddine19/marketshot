from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import translation

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        PRODUCER = 'PRODUCER', _('Studio Team')
        MARKETING = 'MARKETING', _('Marketing Team')
        STORE_OWNER = 'STORE_OWNER', _('Store Owner')
        CUSTOMER = 'CUSTOMER', _('Customer')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER, verbose_name=_("User Role"))
    
    # Localized Personal Names (Optional if you want to separate from Username)
    first_name_ar = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("First Name (AR)"))
    last_name_ar = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Last Name (AR)"))

    # Localized Company/Brand Name
    company_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Company Name"))

    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True)
    
    @property
    def full_name(self):
        lang = translation.get_language()
        if lang == 'ar' and self.first_name_ar:
            return f"{self.first_name_ar} {self.last_name_ar}"
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Bio in 3 Languages السيرة الذاتية (للمنتجين) أو وصف المتجر (لأصحاب المتاجر)
    bio_en = models.TextField(blank=True, null=True, verbose_name=_("Bio (EN)"))
    bio_ar = models.TextField(blank=True, null=True, verbose_name=_("Bio (AR)"))
    bio_fr = models.TextField(blank=True, null=True, verbose_name=_("Bio (FR)"))
    
    # Localized Cities
    city_en = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("City (EN)"))
    city_ar = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("City (AR)"))
    city_fr = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("City (FR)"))

    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Address"))
    
    # روابط التواصل الاجتماعي (مهمة للتسويق والستوديو)
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    instagram = models.URLField(blank=True, null=True, verbose_name=_("Instagram"))
    linkedin = models.URLField(blank=True, null=True, verbose_name=_("LinkedIn"))

    # حقول تقنية
    is_verified = models.BooleanField(default=False, verbose_name=_("Verified Account"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active Account"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    @property
    def city(self):
        lang = translation.get_language()
        if lang == 'ar': return self.city_ar or self.city_en
        if lang == 'fr': return self.city_fr or self.city_en
        return self.city_en

    @property
    def bio(self):
        lang = translation.get_language()
        if lang == 'ar': return self.bio_ar or self.bio_en
        if lang == 'fr': return self.bio_fr or self.bio_en
        return self.bio_en

    def __str__(self):
        return f"Profile: {self.user.username}"