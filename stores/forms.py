from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import Store


class StoreSettingsForm(forms.ModelForm):
    """
    Form for updating store details (name, WhatsApp number, Meta API token).
    Enforces E.164 format for the WhatsApp number.
    """

    whatsapp_number = forms.CharField(
        label=_("WhatsApp number"),
        max_length=17,
        validators=[
            RegexValidator(
                regex=r"^\+[1-9]\d{8,14}$",
                message=_(
                    "Phone number must be in international format (e.g., +14155552671)."
                ),
            )
        ],
        help_text=_("Enter your store's WhatsApp number in international format."),
    )

    class Meta:
        model = Store
        fields = ["name", "whatsapp_number", "meta_api_token"]

    def clean_whatsapp_number(self):
        """Normalize the WhatsApp number by stripping whitespace."""
        number = self.cleaned_data.get("whatsapp_number")
        if number:
            number = number.strip()
        return number
