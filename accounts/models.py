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
    
    username = models.CharField(max_length=150, unique=True, blank=True)
    email = models.EmailField(unique=True, verbose_name=_("Email Address"))
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name=_("Phone Number"))
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER, verbose_name=_("User Role"))
    
    # Localized Personal Names (Optional if you want to separate from Username)
    first_name_ar = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("First Name (AR)"))
    last_name_ar = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Last Name (AR)"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email is required, but not username or password (handled by AbstractUser)
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
    
    @property
    def is_marketing(self):
        return self.role == self.Role.MARKETING
    
    @property
    def is_store_owner(self):
        return self.role == self.Role.STORE_OWNER

    @property
    def is_producer(self):
        return self.role == self.Role.PRODUCER

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def full_name(self):
        lang = translation.get_language()
        if lang == 'ar' and self.first_name_ar:
            return f"{self.first_name_ar} {self.last_name_ar}"
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Wilaya(models.Model):
    code = models.PositiveSmallIntegerField(unique=True)
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    name_fr = models.CharField(max_length=100)

    @property
    def name(self):
        lang = translation.get_language()
        if lang == 'ar': return self.name_ar
        if lang == 'fr': return self.name_fr
        return self.name_en

    def __str__(self):
        return f"{self.code} - {self.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name=_("Avatar"))
    
    # Bio in 3 Languages السيرة الذاتية (للمنتجين) أو وصف المتجر (لأصحاب المتاجر)
    bio_en = models.TextField(blank=True, null=True, verbose_name=_("Bio (EN)"))
    bio_ar = models.TextField(blank=True, null=True, verbose_name=_("Bio (AR)"))
    bio_fr = models.TextField(blank=True, null=True, verbose_name=_("Bio (FR)"))
    
    # Localized Company/Brand Name
    company_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Company Name"))
    wilaya = models.ForeignKey(Wilaya, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Wilaya"))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Address"))
 
    # حقول تقنية
    is_verified = models.BooleanField(default=False, verbose_name=_("Verified Account"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")


    @property
    def bio(self):
        lang = translation.get_language()
        if lang == 'ar': return self.bio_ar or self.bio_en
        if lang == 'fr': return self.bio_fr or self.bio_en
        return self.bio_en

    def __str__(self):
        return f"Profile: {self.user.username}"

