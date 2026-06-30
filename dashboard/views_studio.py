from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.db.models import Count, Sum
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _

from .forms import ProjectForm, ProjectImageFormSet, ServiceForm, PackageForm, PackageFeatureFormSet
from studio.models import Project, Service, Package, Testimonial, ContactMessage, Booking, Subscription


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()

        context.update({

            # totals
            "total_projects": Project.objects.count(),
            "total_services": Service.objects.count(),
            "total_packages": Package.objects.count(),
            "total_bookings": Booking.objects.count(),
            "total_subscriptions": Subscription.objects.count(),
            "total_messages": ContactMessage.objects.count(),

            # booking stats
            "pending_bookings":
                Booking.objects.filter(
                    status="pending"
                ).count(),

            "confirmed_bookings":
                Booking.objects.filter(
                    status="confirmed"
                ).count(),

            "completed_bookings":
                Booking.objects.filter(
                    status="completed"
                ).count(),

            # subscriptions
            "active_subscriptions":
                Subscription.objects.filter(
                    status="active"
                ).count(),

            "expired_subscriptions":
                Subscription.objects.filter(
                    status="expired"
                ).count(),

            # revenue
            "booking_revenue":
                Booking.objects.aggregate(
                    total=Sum("total_price")
                )["total"] or 0,

            "subscription_revenue":
                sum(
                    s.price
                    for s in Subscription.objects.all()
                ),

            # recent activity
            "recent_bookings":
                Booking.objects.select_related(
                    "user",
                    "service"
                )[:5],

            "recent_projects":
                Project.objects[:5],

            "recent_contacts":
                ContactMessage.objects.order_by(
                    "-created_at"
                )[:5],

            "recent_testimonials":
                Testimonial.objects.select_related(
                    "client"
                )[:5],

            "upcoming_bookings":
                Booking.objects.filter(
                    booking_date__gte=today
                )[:8]
        })

        return context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()
        month_ago = today - timedelta(days=30)

        # COUNTS
        context["projects_count"] = Project.objects.count()
        context["services_count"] = Service.objects.filter(is_active=True).count()
        context["packages_count"] = Package.objects.count()

        context["subscriptions_count"] = Subscription.objects.count()
        context["active_subscriptions"] = Subscription.objects.filter(status="active").count()

        context["bookings_count"] = Booking.objects.count()
        context["pending_bookings"] = Booking.objects.filter(status="pending").count()
        
        context["messages_count"] = ContactMessage.objects.count()
        context["unread_messages"] = ContactMessage.objects.filter(is_read=False).count()

        context["testimonials_count"] = Testimonial.objects.count()

        # REVENUE
        context["total_revenue"] = Booking.objects.aggregate(total=Sum("total_price"))["total"] or 0

        # RECENT BOOKINGS
        context["recent_bookings"] = Booking.objects.select_related("user", "service")[:8]

        # RECENT CONTACTS
        context["recent_contacts"] = ContactMessage.objects.order_by("-created_at")[:6]

        # RECENT PROJECTS
        context["recent_projects"] = Project.objects.order_by("-created_at")[:6]

        # UPCOMING BOOKINGS
        context["upcoming_bookings"] = Booking.objects.filter(booking_date__gte=today).order_by("booking_date", "booking_time")[:10]

        # TOP SERVICES
        context["top_services"] = Service.objects.annotate(total_bookings=Count("bookings")).order_by("-total_bookings")[:5]

        return context


class ProjectListView(ListView):
    model = Project
    template_name = "dashboard/studio/projects/list.html"
    context_object_name = "projects"
    paginate_by = 10

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/studio/projects/form.html"
    success_url = reverse_lazy("dashboard:projects")

    def form_valid(self, form):
        inline_images = ProjectImageFormSet(self.request.POST, self.request.FILES)
        if inline_images.is_valid():
            response = super().form_valid(form)
            inline_images.instance = self.object
            inline_images.save()
            messages.success(self.request, _("Project created successfully."))
            return response
        messages.error(self.request, _("Failed to create project."))
        return super().form_valid(form)

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/studio/projects/form.html"
    success_url = reverse_lazy("dashboard:projects")

    def form_valid(self, form):
        inline_images = ProjectImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if inline_images.is_valid():
            response = super().form_valid(form)
            inline_images.save()
            messages.success(self.request, _("Project updated successfully."))
            return response
        messages.error(self.request, _("Failed to update project."))
        return super().form_valid(form)
    
class ProjectDeleteView(DeleteView):
    model = Project
    template_name = "dashboard/studio/projects/delete.html"
    success_url = reverse_lazy("dashboard:projects")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Project deleted successfully."))
        return super().delete(request, *args, **kwargs)


class ServiceManageView(TemplateView):
    template_name = "dashboard/studio/services/manage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = kwargs.get("pk")
        instance = get_object_or_404(Service, pk=pk) if pk else None

        context.update({
            "services": Service.objects.order_by("order"),
            "form": ServiceForm(instance=instance),
            "object": instance,
            "is_editing": bool(instance),
        })

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = get_object_or_404(Service, pk=pk) if pk else None

        form = ServiceForm(
            request.POST,
            request.FILES,
            instance=instance
        )

        if form.is_valid():
            form.save()

            if instance:
                messages.success(
                    request,
                    _("Service updated successfully.")
                )
            else:
                messages.success(
                    request,
                    _("Service created successfully.")
                )

            return redirect("dashboard:services")

        messages.error(
            request,
            _("Failed to save service.")
        )

        context = self.get_context_data(**kwargs)
        context["form"] = form

        return render(
            request,
            self.template_name,
            context
        )
    
class ServiceDeleteView(DeleteView):
    model = Service
    template_name = "dashboard/studio/services/delete.html"
    success_url = reverse_lazy("dashboard:services")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Service deleted successfully."))
        return super().delete(request, *args, **kwargs)
    

class PackageListView(ListView):
    model = Package
    template_name = "dashboard/studio/packages/list.html"
    context_object_name = "packages"
    paginate_by = 10

class PackageCreateView(CreateView):
    model = Package
    form_class = PackageForm
    template_name = "dashboard/studio/packages/form.html"
    success_url = reverse_lazy("dashboard:package-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = PackageFeatureFormSet(self.request.POST)
        else:
            context["formset"] = PackageFeatureFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, _("Package created successfully."))
            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form))

class PackageUpdateView(UpdateView):
    model = Package
    form_class = PackageForm
    template_name = "dashboard/studio/packages/form.html"
    success_url = reverse_lazy("dashboard:package-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = PackageFeatureFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = PackageFeatureFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, _("Package updated successfully."))
            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form))

class PackageDeleteView(DeleteView):
    model = Package
    template_name = "dashboard/studio/packages/delete.html"
    success_url = reverse_lazy("dashboard:package-list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Package deleted successfully."))
        return super().delete(request, *args, **kwargs)


class BookingListView(ListView):
    model = Booking
    template_name = "dashboard/studio/bookings/list.html"
    context_object_name = "bookings"
    ordering = ["-created_at"]

class BookingListView(ListView):
    model = Booking
    template_name = "dashboard/studio/bookings/list.html"
    context_object_name = "bookings"

    def get_queryset(self):
        # Debug: Remove all filters to see if data appears
        return Booking.objects.all()


class SubscriptionListView(ListView):
    model = Subscription
    template_name = "dashboard/studio/subscriptions/list.html"
    context_object_name = "subscriptions"
    ordering = ["-created_at"]


class TestimonialListView(ListView):
    model = Testimonial
    template_name = "dashboard/studio/testimonials/list.html"
    context_object_name = "testimonials"
    ordering = ["-id"]


class ContactMessageListView(ListView):
    model = ContactMessage
    template_name = "dashboard/studio/contacts/list.html"
    context_object_name = "contact_messages"
    ordering = ["-created_at"]

    def get_queryset(self):
        print("Fetching contact messages...")
        print("Total messages in DB:", ContactMessage.objects.count())
        return ContactMessage.objects.order_by("-created_at")

class ContactMessageToggleReadView(TemplateView):
    def post(self, request, pk):
        message = get_object_or_404(ContactMessage, pk=pk)
        if message.is_read:
            message.is_read = False
            message.save()
            messages.info(request, _("Message marked as unread."))
        else:
            message.is_read = True
            message.save()
            messages.success(request, _("Message marked as read."))
        return redirect("dashboard:contact-list")

