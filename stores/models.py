import uuid
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Store(models.Model):
    """
    Represents a tenant in the multi‑tenant architecture.
    All business data (products, orders, customers) will be linked to a Store.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the store (tenant)."),
    )
    name = models.CharField(
        _("store name"),
        max_length=200,
        unique=True,
        db_index=True,
        help_text=_("Unique name of the store."),
    )
    whatsapp_number = models.CharField(
        _("WhatsApp number"),
        max_length=17,  # E.164 max length: + and up to 15 digits
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^\+[1-9]\d{8,14}$",
                message=_(
                    "Phone number must be in international format (e.g., +14155552671)."
                ),
            )
        ],
        help_text=_("Store's WhatsApp number in international format."),
    )
    meta_api_token = models.CharField(
        _("Meta API token"),
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text=_("Token for Meta API integrations. Generated later."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this store is active. Unselect this instead of deleting.",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("store")
        verbose_name_plural = _("stores")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name", "whatsapp_number"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """
        Normalize and validate store fields before saving.
        """
        super().clean()

        # Normalize WhatsApp number (strip spaces)
        if self.whatsapp_number:
            self.whatsapp_number = self.whatsapp_number.strip()

        # Normalize store name (strip leading/trailing whitespace)
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError({"name": _("Store name cannot be blank.")})

        # Convert empty meta_api_token to None to avoid empty strings in unique field
        if self.meta_api_token is not None and self.meta_api_token.strip() == "":
            self.meta_api_token = None

    def save(self, *args, **kwargs):
        """Enforce full validation before every save."""
        self.full_clean()
        super().save(*args, **kwargs)
