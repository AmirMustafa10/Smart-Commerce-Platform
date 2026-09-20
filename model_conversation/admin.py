from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Conversation, ChatMessage


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer__name", "customer__phone_number")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("customer",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin configuration for the ChatMessage model."""

    list_display = (
        "get_customer_name",
        "get_customer_phone",
        "sender",
        "short_text",
        "timestamp",
    )
    list_filter = ("sender", "timestamp")
    search_fields = (
        "conversation__customer__name",
        "conversation__customer__phone_number",
        "text",
    )
    readonly_fields = ("id", "timestamp")

    autocomplete_fields = ("conversation",)

    fieldsets = (
        (
            _("Basic Info"),
            {"fields": ("id", "conversation", "sender", "text")},
        ),
        (_("Timestamps"), {"fields": ("timestamp",)}),
    )

    @admin.display(description=_("Customer Name"))
    def get_customer_name(self, obj):
        return obj.conversation.customer.name

    @admin.display(description=_("Phone Number"))
    def get_customer_phone(self, obj):
        return obj.conversation.customer.phone_number

    @admin.display(description=_("Text"))
    def short_text(self, obj):
        return f"{obj.text[:50]}..." if len(obj.text) > 50 else obj.text

    def has_delete_permission(self, request, obj=None):
        return False
