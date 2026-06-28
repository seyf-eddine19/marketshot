from django.contrib import admin
from django.utils import timezone
from .models import Project, ProjectImage, Testimonial, ContactMessage, Service, Package, PackageFeature, Subscription, Booking

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    inlines = [ProjectImageInline]

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client', 'rating', 'is_active', 'created_at')
    search_fields = ('client__username', 'feedback')
    list_filter = ('is_active', 'created_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('is_read', 'created_at')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'color_class', 'order')
    search_fields = ('title', 'title_ar', 'title_fr', 'description', 'description_ar', 'description_fr')
    list_filter = ('color_class',)

class PackageFeatureInline(admin.TabularInline):
    model = PackageFeature
    extra = 1

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_price', 'discount', 'get_price', 'is_active', 'created_at')
    search_fields = ('title_ar', 'title_en', 'title_fr', 'description_ar', 'description_en', 'description_fr')
    list_filter = ('is_active', 'is_highlighted', 'created_at')
    inlines = [PackageFeatureInline]

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'status', 'created_at')
    search_fields = ('user__username', 'package__title')
    list_filter = ('status', 'created_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'booking_date', 'booking_time', 'status', 'created_at')
    search_fields = ('user__username', 'service__title', 'location', 'notes')
    list_filter = ('status', 'booking_date', 'created_at')

    def booking_status(self, obj):
        if obj.booking_date < timezone.now().date():
            return "Past"
        elif obj.booking_date == timezone.now().date():
            return "Today"
        else:
            return "Upcoming"
    
    booking_status.short_description = 'Booking Status'