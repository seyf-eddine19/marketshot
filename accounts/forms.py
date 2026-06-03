from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class UserRegistrationForm(UserCreationForm):
    # We explicitly add fields we want the user to fill during signup
    role = forms.ChoiceField(
        choices=[(User.Role.STORE_OWNER, _('Store Owner')), (User.Role.CUSTOMER, _('Customer'))],
        label=_("Register as")
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "company_name", "first_name", "last_name", "password1", "password2")

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username')}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Password')}))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "company_name", "first_name", "last_name", "phone", "avatar")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'watsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control'}),
        }