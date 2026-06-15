from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm, UserLoginForm

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from .forms import UserUpdateForm, UserProfileForm

from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy


class SignUpView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('profile')

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Welcome back 👋")
        return response

    def get_success_url(self):
        return reverse_lazy('dashboard:dashboard') 

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form
        })

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("profile")

        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form
        })


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("password_change_done")


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "accounts/change_password_done.html"