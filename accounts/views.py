from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.db.models import Q
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, UpdateView
from django.utils.translation import gettext_lazy as _
from stores.models import Store
from django.contrib.auth import get_user_model
from .forms import MerchantSignUpForm, ShipperCreationForm, UserProfileUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.contrib import messages
from core.models import OwnerRequiredMixin

CustomUser = get_user_model()


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
        )  # pyright: ignore[reportCallIssue]

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


class TeamListView(LoginRequiredMixin, ListView):
    """
    List all shippers belonging to the current owner's store with search functionality.
    """

    model = CustomUser
    template_name = "accounts/team_list.html"
    context_object_name = "shippers"

    def get_queryset(self):
        """
        Strictly filter to shippers of the current user's store,
        and apply search filtering if a query is provided.
        """
        qs = CustomUser.objects.filter(
            store=self.request.user.store,
            role=CustomUser.Role.SHIPPER,
        )

        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            qs = qs.filter(
                Q(full_name__icontains=search_query) | Q(email__icontains=search_query)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = CustomUser.objects.filter(
            store=self.request.user.store, role=CustomUser.Role.OWNER
        ).first()
        return context


class ShipperCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    """
    Create a new shipper under the current owner's store.
    """

    model = CustomUser
    form_class = ShipperCreationForm
    template_name = "accounts/shipper_form.html"
    success_url = reverse_lazy("accounts:team_list")

    def get_form_kwargs(self):
        """
        assign the store and role automatically.
        """
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = CustomUser(
            store=self.request.user.store, role=CustomUser.Role.SHIPPER
        )
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Shipper added successfully."))
        return super().form_valid(form)


class ShipperToggleStatusView(LoginRequiredMixin, OwnerRequiredMixin, View):
    """
    Toggle the is_active status of a shipper.
    Only accessible via POST to prevent accidental changes.
    """

    def post(self, request, pk, *args, **kwargs):
        shipper = get_object_or_404(
            CustomUser, pk=pk, store=request.user.store, role=CustomUser.Role.SHIPPER
        )

        shipper.is_active = not shipper.is_active
        shipper.save()

        if shipper.is_active:
            messages.success(request, f"Shipper '{shipper.full_name}' is now Active.")
        else:
            messages.warning(
                request, f"Shipper '{shipper.full_name}' has been Deactivated."
            )

        return redirect("accounts:team_list")


class MemberProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "accounts/member_profile.html"
    context_object_name = "member"

    def get_object(self, queryset=None):
        if "pk" in self.kwargs:
            return get_object_or_404(
                CustomUser,
                pk=self.kwargs["pk"],
                store=self.request.user.store,
            )

        return self.request.user


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for any logged-in user to update their own profile.
    """

    model = CustomUser
    form_class = UserProfileUpdateForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:my_profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Your profile has been updated successfully."))
        return super().form_valid(form)

class CustomPasswordChangeView(PasswordChangeView):
    """
    Secure view for changing the password.
    Uses Django's built-in form and logic for maximum security.
    """
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy('accounts:my_profile') 

    def form_valid(self, form):
        messages.success(self.request, _("Your password has been successfully updated!"))
        return super().form_valid(form)
