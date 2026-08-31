from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Store


class StoreAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Store (tenant) model.
    """

    list_display = ("name", "whatsapp_number", "created_at", "updated_at", "is_active")
    search_fields = ("name", "whatsapp_number")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("name",)
    list_filter = ("created_at", "is_active")

    def get_exclude(self, request, obj=None):
        """
        Completely hide 'meta_api_token' from non-superusers.
        """
        excluded = super().get_exclude(request, obj) or []
        excluded = list(excluded)

        if not request.user.is_superuser:
            excluded.append("meta_api_token")

        return tuple(excluded)


admin.site.register(Store, StoreAdmin)
