from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.utils.translation import gettext_lazy as _
from stores.models import Store
from .models import CustomUser
from .forms import MerchantSignUpForm
from django.contrib import messages


class MerchantSignUpView(FormView):
    """
    Handle merchant self‑registration.
    Creates the Store and the CustomUser (role=OWNER) atomically,
    then logs the user in and redirects to the dashboard.
    """

    template_name = "accounts/signup.html"
    form_class = MerchantSignUpForm
    success_url = reverse_lazy("core:dashboard")

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect("core:dashboard")

        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        # 1. Create the Store (tenant)
        store = Store.objects.create(
            name=form.cleaned_data["store_name"],
            whatsapp_number=form.cleaned_data["whatsapp_number"],
        )

        # 2. Create the CustomUser with role=OWNER
        user = CustomUser.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            full_name=form.cleaned_data["full_name"],
            store=store,
            role=CustomUser.Role.OWNER,
        )

        # 3. Log the user in
        login(self.request, user)

        # Add success message
        messages.success(
            self.request, _("Registration successful! Welcome to your dashboard.")
        )
        return super().form_valid(form)


class MerchantLoginView(LoginView):
    """
    Custom login view that redirects authenticated users to dashboard.
    """

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("core:dashboard")
