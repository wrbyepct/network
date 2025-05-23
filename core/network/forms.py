"""User forms."""

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class SignupForm(UserCreationForm):
    """User form."""

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        label=_("Password"),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        label=_("Confirmation"),
        help_text=_("Enter the same password again for verification."),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
