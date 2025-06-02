"""Profile form."""

from django import forms
from django.forms.widgets import DateInput
from phonenumber_field.formfields import SplitPhoneNumberField

from .models import Profile


class ProfileForm(forms.ModelForm):
    """Profile form."""

    phonenumber = SplitPhoneNumberField(
        required=False,
        initial="TW",
    )
    birth_date = forms.DateField(
        widget=DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = Profile
        fields = [
            "username",
            "profile_picture",
            "first_name",
            "last_name",
            "phonenumber",
            "bio",
            "birth_date",
        ]
