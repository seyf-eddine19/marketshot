from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm, UserLoginForm

class SignUpView(CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        # Auto-login the user after registration (Optional)
        user = form.save()
        login(self.request, user)
        return redirect('profile_setup') # Redirect to a setup page or home

class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        # Logic to redirect based on Role
        user = self.request.user
        if user.role == user.Role.ADMIN:
            return reverse_lazy('admin_dashboard')
        if user.role == user.Role.PRODUCER:
            return reverse_lazy('studio_dashboard')
        return reverse_lazy('home')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class ProfileView(CreateView):
    form_class = UserRegistrationForm  # You can create a separate form for profile setup if needed
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('dashboard')  # Redirect to dashboard after setup

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # Pre-fill the form with existing user data
        user = self.request.user
        form.fields['username'].initial = user.username
        form.fields['email'].initial = user.email
        form.fields['company_name'].initial = user.company_name
        form.fields['first_name'].initial = user.first_name
        form.fields['last_name'].initial = user.last_name
        return form

    def form_valid(self, form):
        # Update the user's profile with the new data
        user = self.request.user
        user.username = form.cleaned_data['username']
        user.email = form.cleaned_data['email']
        user.company_name = form.cleaned_data['company_name']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        return super().form_valid(form)