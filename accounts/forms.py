from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[(User.Role.STORE_OWNER, _('Store Owner')), (User.Role.CUSTOMER, _('Customer'))],
        label=_("Register as")
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email", "first_name", "last_name", "first_name_ar", "last_name_ar", 
            "role",  "phone", "password1", "password2"
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.username = self.cleaned_data['email'].split('@')[0]  # Use email prefix as username
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-3 border rounded-lg',
            'placeholder': 'Email'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-3 border rounded-lg',
            'placeholder': 'Password'
        })
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "first_name_ar", "last_name_ar", "phone")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("avatar", "bio_ar", "bio_en", "bio_fr", "company_name", "wilaya", "address")

