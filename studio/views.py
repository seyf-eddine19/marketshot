from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, CreateView
from studio.models import Project, Service, Package, Testimonial, ContactMessage, Booking

class StudioHomeView(TemplateView):
    template_name = "studio/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.prefetch_related('images').all().order_by('-created_at')[:6]
        context['services'] = Service.objects.all().order_by('order')
        context["packages"] = Package.objects.prefetch_related("features").filter(is_active=True)
        context['testimonials'] = Testimonial.objects.filter(is_active=True).order_by('-created_at')[:3]
        return context
    
    def post(self, request, *args, **kwargs):
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )

        messages.success(
            request,
            _("Your message has been sent successfully.")
        )

        return redirect("studio:home")
    
class ContactView(TemplateView):
    template_name = "studio/pages/contact.html"

class BookingView(TemplateView):
    template_name = "studio/pages/booking.html"



class BookingPageView(TemplateView):
    template_name = "studio/booking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = Service.objects.filter(is_active=True).order_by("order")
        return context


class BookingCreateView(CreateView):
    model = Booking
    fields = [
        "service",
        "booking_date",
        "booking_time",
        "duration",
        "location",
        "notes",
    ]
    template_name = "studio/booking_form.html"
    template_name = "booking/studio_booking.html"
    success_url = reverse_lazy("studio:booking")

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Optional: calculate price placeholder
        form.instance.total_price = 0

        messages.success(self.request, "Booking created successfully!")
        return super().form_valid(form)
    
    from django.views.generic import TemplateView
from .models import Service, Package


class BookingCreateView(TemplateView):
    template_name = "studio/booking_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["services"] = Service.objects.filter(is_active=True)
        context["packages"] = Package.objects.filter(is_active=True)

        # default selections (for UI highlight like your design)
        context["selected_service"] = context["services"].first()
        context["selected_package"] = context["packages"].first()

        return context