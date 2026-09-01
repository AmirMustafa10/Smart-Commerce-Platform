from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from stores.models import Store

CustomUser = get_user_model()


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


class MerchantSignUpForm(forms.Form):
    """
    Form for merchant self‑registration.
    Collects store name, full name, email, and password.
    Validates uniqueness and password matching.
    """

    store_name = forms.CharField(
        max_length=200,
        label=_("Store name"),
        help_text=_("Required. Unique name for your store."),
    )
    full_name = forms.CharField(
        max_length=150,
        label=_("Full name"),
    )
    email = forms.EmailField(
        label=_("Email"),
        help_text=_("Will be used as your login identifier."),
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label=_("Password"),
        strip=False,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label=_("Confirm password"),
        strip=False,
    )
    whatsapp_number = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\+[1-9]\d{8,14}$",
                message=_(
                    "Phone number must be in international format (e.g., +14155552671)."
                ),
            )
        ],
        widget=forms.TextInput(attrs={"placeholder": "+201000000000"}),
    )

    def clean_store_name(self):
        """Validate that the store name is unique (case‑insensitive)."""
        store_name = self.cleaned_data.get("store_name")
        if store_name:
            store_name = store_name.strip()
            if Store.objects.filter(name__iexact=store_name).exists():
                raise ValidationError(_("A store with this name already exists."))
        return store_name

    def clean_whatsapp_number(self):
        whatsapp_number = self.cleaned_data.get("whatsapp_number")

        if Store.objects.filter(whatsapp_number=whatsapp_number).exists():
            raise ValidationError("A store with this WhatsApp number already exists.")

        return whatsapp_number

    def clean_email(self):
        """Normalize email and check uniqueness (case‑insensitive)."""
        email = self.cleaned_data.get("email")
        if email:
            email = email.strip().lower()
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise ValidationError(_("A user with this email already exists."))
        return email

    def clean(self):
        """Ensure password and confirmation match."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError({"confirm_password": _("Passwords do not match.")})
        return cleaned_data


class ShipperCreationForm(forms.ModelForm):
    """
    Form for creating a new shipper account.
    Exposes only full_name, email, and password.
    Store and role are set automatically in the view.
    """

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter a strong password for the shipper."),
    )

    class Meta:
        model = CustomUser
        fields = ["full_name", "email"]

    def clean_email(self):
        """Normalize email and ensure uniqueness."""
        email = self.cleaned_data.get("email")
        if email:
            email = email.strip().lower()
            # Check if already exists
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError(_("A user with this email already exists."))
        return email

    def save(self, commit=True):
        """
        Override save to set the password using the manager's create_user logic.
        We do not save the instance directly because the password is not a model field.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
