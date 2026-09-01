from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    """
    Custom admin for CustomUser, replacing the default username-based admin.
    """

    # Use our custom forms
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = CustomUser

    # Fields to display in the list view
    list_display = ("email", "full_name", "store", "role", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "role", "store")
    search_fields = ("email", "full_name", "store__name")
    ordering = ("email",)
    readonly_fields = ("date_joined", "id")

    # Fieldsets for editing an existing user (change view)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name", "store", "role")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Fieldsets for adding a new user (add view)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "store",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Make sure email is used as the identifier (no username)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remove 'username' if it accidentally appears (defensive)
        if "username" in form.base_fields:
            del form.base_fields["username"]
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Ensure no username field sneaks in (defensive)
        for fieldset in fieldsets:
            if "username" in fieldset[1]["fields"]:
                fieldset[1]["fields"] = tuple(
                    f for f in fieldset[1]["fields"] if f != "username"
                )
        return fieldsets


admin.site.register(CustomUser, CustomUserAdmin)
