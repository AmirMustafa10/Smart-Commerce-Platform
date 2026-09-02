from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, View
from django.utils.translation import gettext_lazy as _
from .models import Store
from core.models import OwnerRequiredMixin
from .forms import StoreSettingsForm


class StoreSettingsView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """
    Allow a store owner to update their store's settings.
    The store is always taken from the authenticated user's `store` field,
    never from a URL parameter (prevents IDOR).
    """

    model = Store
    form_class = StoreSettingsForm
    template_name = "stores/settings.html"
    success_url = reverse_lazy("stores:settings")  # stay on same page after update

    def get_object(self, queryset=None):
        """
        Return the store belonging to the current user.
        This overrides the default behavior of retrieving by pk/slug.
        """
        return self.request.user.store

    def form_valid(self, form):
        """Save the form and add a success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("Store settings updated successfully."))
        return response


class StoreDeactivateView(LoginRequiredMixin, OwnerRequiredMixin, View):
    """
    Deactivate the user's store (soft delete) and log out the user.
    Only accessible via POST.
    """

    def post(self, request, *args, **kwargs):
        store = request.user.store
        store.is_active = False
        store.save(update_fields=["is_active"])  # update only the flag

        messages.success(
            request, _("Your store has been deactivated.")
        )
        return redirect("stores:settings")


class StoreActivateView(LoginRequiredMixin, OwnerRequiredMixin, View):
    """
    Activate the user's store.
    Only accessible via POST.
    """

    def post(self, request, *args, **kwargs):
        store = request.user.store
        store.is_active = True
        store.save(update_fields=["is_active"])  # update only the flag

        messages.success(request, _("Your store has been activated."))
        return redirect("stores:settings")
