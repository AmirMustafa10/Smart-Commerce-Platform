from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Store


class StoreAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Store (tenant) model.
    """

    list_display = ("name", "whatsapp_number", "created_at", "updated_at")
    search_fields = ("name", "whatsapp_number")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("name",)
    list_filter = ("created_at",)

    def get_readonly_fields(self, request, obj=None):
        """
        Dynamically make 'meta_api_token' read-only for non-superusers.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))

        # if user is staff not superuser
        if not request.user.is_superuser:
            readonly_fields.append("meta_api_token")

        return tuple(readonly_fields)


admin.site.register(Store, StoreAdmin)
