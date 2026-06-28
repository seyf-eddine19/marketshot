from django.db import models
from django.utils import translation, timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from decimal import Decimal

from accounts.models import User


class Project(models.Model):
    title_ar = models.CharField(max_length=255, verbose_name=_("Title (Arabic)"))
    title_en = models.CharField(max_length=255, verbose_name=_("Title (English)"))
    title_fr = models.CharField(max_length=255, verbose_name=_("Title (French)"))

    description_ar = models.TextField(verbose_name=_("Description (Arabic)"))
    description_en = models.TextField(verbose_name=_("Description (English)"))
    description_fr = models.TextField(verbose_name=_("Description (French)"))
    
    image = models.ImageField(upload_to='portfolio/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'avif', 'webp'])], blank=True, null=True, verbose_name=_("Main Image"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-created_at']

    @property
    def title(self):
        lang = translation.get_language()
        if lang == 'ar': return self.title_ar  or self.title_en
        if lang == 'fr': return self.title_fr  or self.title_en
        return self.title_en

    @property
    def description(self):
        lang = translation.get_language()
        if lang == 'ar': return self.description_ar or self.description_en
        if lang == 'fr': return self.description_fr or self.description_en
        return self.description_en

    def __str__(self):
        return self.title
    
class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images', verbose_name=_("Project"))
    image = models.ImageField(upload_to='portfolio/', verbose_name=_("Image"))
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Caption"))

    def __str__(self):
        return f"Image for {self.project.title}"


class Testimonial(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials', verbose_name=_("Client"))
    feedback = models.TextField(verbose_name=_("Feedback"))
    rating = models.PositiveIntegerField(default=5, verbose_name=_("Rating"), help_text=_("Rating from 1 to 5"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        ordering = ['-created_at', 'rating']

    def __str__(self):
        return f"Testimonial by {self.client.username} - Rating: {self.rating}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    email = models.EmailField(verbose_name=_("Email"))
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    message = models.TextField(verbose_name=_("Message"))

    is_read = models.BooleanField(default=False, verbose_name=_("Is Read"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"Message from {self.name} - Subject: {self.subject}"
    
# ----------------------------
# Service Model
# ----------------------------
class Service(models.Model):

    ICON_CHOICES = [
        ("photo_camera", _("Photography")),
        ("videocam", _("Video")),
        ("diversity_3", _("UGC")),
        ("trending_up", _("Marketing")),
        ("brush", _("Design")),
        ("mic", _("Voice Over")),
        ("location_on", _("Field Shooting")),
        ("camera_indoor", _("Studio Rental")),
        ("hub", _("Platform")),
    ]

    COLOR_CHOICES = [
        ("primary", _("Primary")),
        ("secondary", _("Secondary")),
    ]

    title_ar = models.CharField(max_length=255, verbose_name=_("Title (Arabic)"))
    title_en = models.CharField(max_length=255, verbose_name=_("Title (English)"))
    title_fr = models.CharField(max_length=255, verbose_name=_("Title (French)"))

    description_ar = models.TextField(max_length=1500, verbose_name=_("Description (Arabic)"))
    description_en = models.TextField(max_length=1500, verbose_name=_("Description (English)"))
    description_fr = models.TextField(max_length=1500, verbose_name=_("Description (French)"))

    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default="photo_camera", verbose_name=_("Icon"))
    color_class = models.CharField(max_length=50, choices=COLOR_CHOICES, default="primary", verbose_name=_("Color"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    order = models.IntegerField(default=0, verbose_name=_("Display Order"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ["order", "created_at"]

    @property
    def title(self):
        lang = translation.get_language()
        if lang == 'ar': return self.title_ar  or self.title_en
        if lang == 'fr': return self.title_fr  or self.title_en
        return self.title_en
    
    @property
    def description(self):
        lang = translation.get_language()
        if lang == 'ar': return self.description_ar or self.description_en
        if lang == 'fr': return self.description_fr or self.description_en
        return self.description_en
        
    def __str__(self):
        return self.title


# ----------------------------
# Package Model
# ----------------------------
class Package(models.Model):
    title_ar = models.CharField(max_length=255, verbose_name=_("Title (Arabic)"))
    title_en = models.CharField(max_length=255, verbose_name=_("Title (English)"))
    title_fr = models.CharField(max_length=255, verbose_name=_("Title (French)"))

    description_ar = models.TextField(verbose_name=_("Description (Arabic)"))
    description_en = models.TextField(verbose_name=_("Description (English)"))
    description_fr = models.TextField(verbose_name=_("Description (French)"))
    
    base_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Base Price"))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True, verbose_name=_("Discount"))

    is_highlighted = models.BooleanField(default=False, verbose_name=_("Is Highlighted"))
    button_link = models.URLField(blank=True, null=True, verbose_name=_("Button Link"))

    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Package")
        verbose_name_plural = _("Packages")
        ordering = ["order", "created_at"]
        
    @property
    def title(self):
        lang = translation.get_language()
        if lang == 'ar': return self.title_ar  or self.title_en
        if lang == 'fr': return self.title_fr  or self.title_en
        return self.title_en
    
    @property
    def description(self):
        lang = translation.get_language()
        if lang == 'ar': return self.description_ar or self.description_en
        if lang == 'fr': return self.description_fr or self.description_en
        return self.description_en

    @property
    def get_current_price(self):
        """يحسب السعر بعد الخصم المئوي"""
        if self.base_price and self.discount and self.discount > 0:
            discount_amount = self.base_price * (self.discount / Decimal('100'))
            return self.base_price - discount_amount
        return self.base_price

    @property
    def has_discount(self):
        """التحقق من وجود خصم صالح وصحيح"""
        return self.discount and self.discount > 0

    def get_price(self, duration='monthly'):
        base_price = self.base_price or Decimal('0')
        discount = self.discount or Decimal('0')
        if duration == 'yearly':
            base_price *= Decimal('12')
        price = base_price * (Decimal('1') - (discount / Decimal('100')))
        return price.quantize(Decimal('0.01'))

    def __str__(self):
        return self.title

class PackageFeature(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="features")

    text_ar = models.CharField(max_length=255, verbose_name=_("Text (Arabic)"))
    text_en = models.CharField(max_length=255, verbose_name=_("Text (English)"))
    text_fr = models.CharField(max_length=255, verbose_name=_("Text (French)"))

    is_included = models.BooleanField(default=True, verbose_name=_("Is Included"))

    class Meta:
        verbose_name = _("Package Feature")
        verbose_name_plural = _("Package Features")
    
    @property
    def text(self):
        lang = translation.get_language()
        if lang == 'ar': return self.text_ar  or self.text_en
        if lang == 'fr': return self.text_fr  or self.text_en
        return self.text_en

    def __str__(self):
        return f"{self.package.title} - {self.text}"


# ----------------------------
# Subscription Model
# ----------------------------
class Subscription(models.Model):

    DURATION_CHOICES = [
        ('monthly', _("Monthly")),
        ('yearly', _("Yearly")),
    ]

    STATUS_CHOICES = [
        ('active', _("Active")),
        ('paused', _("Paused")),
        ('cancelled', _("Cancelled")),
        ('expired', _("Expired")),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_("User"))
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_("Package"))

    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))

    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='monthly', verbose_name=_("Duration"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_("Status"))

    auto_renew = models.BooleanField(default=True, verbose_name=_("Auto Renew"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ['-created_at']

    @property
    def remaining_days(self):
        return max((self.end_date - timezone.now().date()).days, 0)

    @property
    def is_expired(self):
        return timezone.now().date() > self.end_date

    @property
    def price(self):
        return self.package.get_price(self.duration)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.package.title} ({self.get_duration_display()})"


# ----------------------------
# Booking Model
# ----------------------------
class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', _("Pending")),
        ('confirmed', _("Confirmed")),
        ('in_progress', _("In Progress")),
        ('completed', _("Completed")),
        ('cancelled', _("Cancelled")),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name=_("User"))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings', verbose_name=_("Service"))
    booking_date = models.DateField(verbose_name=_("Booking Date"))
    booking_time = models.TimeField(verbose_name=_("Booking Time"))
    duration = models.PositiveIntegerField(verbose_name=_("Duration (Minutes)"))
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Location"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Total Price"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")
        ordering = ["-booking_date", "-booking_time"]

    @property
    def is_past(self):
        from datetime import datetime
        booking_datetime = datetime.combine(self.booking_date, self.booking_time)
        return booking_datetime < datetime.now()

    def __str__(self):
        return (f"{self.user.username} - {self.service.title} ({self.booking_date})")