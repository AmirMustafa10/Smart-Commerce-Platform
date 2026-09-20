from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model."""

    list_display = (
        "customer__name",
        "customer__phone_number",
        "sender",
        "text",
        "timestamp",
    )
    list_filter = ("timestamp",)
    search_fields = ("customer__name", "customer__phone_number", "text")
    readonly_fields = ("id", "timestamp")

    # Autocomplete for large datasets: requires search_fields on the related admins.
    autocomplete_fields = ("customer",)

    fieldsets = (
        (
            _("Basic Info"),
            {"fields": ("id", "customer")},
        ),
        (_("Timestamps"), {"fields": ("timestamp",)}),
    )

    def has_delete_permission(self, request, obj=None):
        return False
