from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new CustomUser in the admin.
    Inherits from UserCreationForm but replaces username with email and adds our custom fields.
    """

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "full_name", "store", "role")
        # Password1 and password2 are inherited automatically from UserCreationForm


class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating an existing CustomUser in the admin.
    Points to our CustomUser model and includes all relevant fields.
    """

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = "__all__"  # Includes all fields except password (handled separately by UserChangeForm)
