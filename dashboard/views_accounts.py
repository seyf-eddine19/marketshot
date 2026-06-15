from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db import transaction
from django.db.models import Q

from .forms import UserUpdateForm, UserProfileForm
from accounts.models import User, UserProfile

class UserListView(LoginRequiredMixin, ListView):
    template_name = "dashboard/users/list.html"
    model = User
    context_object_name = "users"
    paginate_by = 30

    def get_queryset(self):
        queryset = User.objects.select_related('profile', 'profile__wilaya').order_by('-profile__created_at')
        
        # 1. Handle Role Filtering
        role_filter = self.request.GET.get('role')
        if role_filter in User.Role.values:
            queryset = queryset.filter(role=role_filter)
            
        # 2. Handle Text Search Matching Max Structural Fields
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(first_name_ar__icontains=query) |
                Q(last_name_ar__icontains=query) |
                Q(profile__company_name__icontains=query) |
                Q(profile__wilaya__name_en__icontains=query) |
                Q(profile__wilaya__name_ar__icontains=query)
            ).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users_count'] = self.get_queryset().count()
        return context


class UserCreateView(LoginRequiredMixin, CreateView):
    template_name = "dashboard/users/form.html"
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('dashboard:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = UserProfileForm(self.request.POST, self.request.FILES)
        else:
            context['profile_form'] = UserProfileForm()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        
        if profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Save core User instance
                    self.object = form.save()
                    
                    # Create or fetch matching UserProfile instance seamlessly
                    profile, created = UserProfile.objects.get_or_create(user=self.object)
                    
                    # Bind the secondary form data over the profile record
                    profile_form = UserProfileForm(self.request.POST, self.request.FILES, instance=profile)
                    profile_form.save()
                    
                messages.success(self.request, _("User account and profile created successfully."))
                return redirect(self.get_success_url())
            except Exception as e:
                form.add_error(None, f"An unexpected database error occurred: {str(e)}")
        
        return self.form_invalid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "dashboard/users/form.html"
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('dashboard:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Safely fetch or initialize a profile record if missing from legacy records
        profile, created = UserProfile.objects.get_or_create(user=self.object)
        
        if self.request.POST:
            context['profile_form'] = UserProfileForm(self.request.POST, self.request.FILES, instance=profile)
        else:
            context['profile_form'] = UserProfileForm(instance=profile)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        
        if profile_form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                profile_form.save()
            messages.success(self.request, _("User settings updated successfully."))
            return redirect(self.get_success_url())
        
        return self.form_invalid(form)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "dashboard/users/delete.html"
    model = User
    success_url = reverse_lazy('dashboard:user_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("User database records purged successfully."))
        return super().delete(request, *args, **kwargs)