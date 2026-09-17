from django.contrib import messages
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views.generic.edit import DeleteView
from .forms import OrderForm, OrderStatusForm, OrderItemFormSet, ShipperOrderStatusForm
from .models import Order
from core.models import (
    StoreManagerRequiredMixin,
    TenantQuerySetMixin,
    ShipperRequiredMixin,
)

CustomUser = get_user_model()


# ---------------------------------------------------------------------------
# List View
# ---------------------------------------------------------------------------
class OrderListView(LoginRequiredMixin, TenantQuerySetMixin, ListView):
    """
    List orders dynamically based on user role:
    - Managers/Owners see all store orders (and can filter soft-deleted).
    - Shippers see only their assigned active orders.
    """

    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user

        if user.role in [user.Role.MANAGER, user.Role.OWNER]:
            qs = Order.all_objects.filter(store=user.store)

        elif user.role == user.Role.SHIPPER:
            qs = super().get_queryset().filter(shipper=user)

        else:
            return Order.objects.none()

        # use `select_related` for performance.
        qs = qs.select_related("customer", "shipper")

        status = self.request.GET.get("status")
        search_query = self.request.GET.get("search")

        if status:
            # We don't want the representative to see the [DELETED] data; that’s for the manager only.
            if status == "DELETED" and user.role in [
                user.Role.MANAGER,
                user.Role.OWNER,
            ]:
                qs = qs.filter(is_deleted=True)
            else:
                qs = qs.filter(status=status, is_deleted=False)

        if search_query:
            qs = qs.filter(
                Q(id__icontains=search_query)
                | Q(customer__name__icontains=search_query)
                | Q(customer__phone_number__icontains=search_query)
            )

        return qs.prefetch_related("items__product")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_orders"] = ctx["paginator"].count
        return ctx


# ---------------------------------------------------------------------------
# Detail View
# ---------------------------------------------------------------------------
class OrderDetailView(LoginRequiredMixin, TenantQuerySetMixin, DetailView):
    """
    Display full details of a specific order.
    Handles visibility dynamically based on user role.
    """

    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.SHIPPER:
            qs = super().get_queryset().filter(
                Q(shipper=user) | Q(shipper__isnull=True, status=Order.Status.PREPARING)
            )
        elif user.role in [user.Role.MANAGER, user.Role.OWNER]:
            qs = Order.all_objects.filter(store=user.store)
        else:
            qs = Order.objects.none()

        # 3. Optimization: To retrieve the customer, representative, and products in a single query.
        return qs.select_related("customer", "shipper").prefetch_related(
            "items__product"
        )


# ---------------------------------------------------------------------------
# Create View
# ---------------------------------------------------------------------------
class OrderCreateView(LoginRequiredMixin, StoreManagerRequiredMixin, CreateView):
    """
    Create an Order along with its OrderItems atomically.
    Both the OrderForm AND the OrderItemFormSet must be valid.
    """

    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("orders:order_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["store"] = self.request.user.store
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = OrderItemFormSet(
                self.request.POST, instance=self.object, store=self.request.user.store
            )
        else:
            ctx["formset"] = OrderItemFormSet(
                instance=self.object, store=self.request.user.store
            )
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = OrderItemFormSet(
            request.POST, instance=None, store=request.user.store
        )
        if form.is_valid() and formset.is_valid():
            return self._forms_valid(form, formset)
        return self._forms_invalid(form, formset)

    @transaction.atomic
    def _forms_valid(self, form, formset):
        # Save the order first, then attach items.
        form.instance.store = self.request.user.store
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        messages.success(self.request, _("Order created successfully."))
        return HttpResponseRedirect(self.get_success_url())

    def _forms_invalid(self, form, formset):
        messages.error(self.request, _("Please correct the errors below."))
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


# ---------------------------------------------------------------------------
# Update View (handles frozen vs editable orders)
# ---------------------------------------------------------------------------
class OrderUpdateView(
    LoginRequiredMixin, TenantQuerySetMixin, StoreManagerRequiredMixin, UpdateView
):
    """
    Update an Order.
    - If the order is frozen (SHIPPED/DELIVERED/CANCELLED), only `status` and `notes`
    can be updated. Items are shown read-only.
    - Otherwise, the full OrderForm + OrderItemFormSet is used.
    """

    model = Order
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("orders:order_list")

    def get_form_class(self):
        return OrderStatusForm if self.object.is_frozen else OrderForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.object.is_frozen:
            kwargs["store"] = self.request.user.store
            kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.object.is_frozen:
            # Read-only display of items.
            ctx["formset"] = None
            ctx["items"] = self.object.items.select_related("product").all()
        else:
            if self.request.POST:
                ctx["formset"] = OrderItemFormSet(
                    self.request.POST,
                    instance=self.object,
                    store=self.request.user.store,
                )
            else:
                ctx["formset"] = OrderItemFormSet(
                    instance=self.object, store=self.request.user.store
                )
        ctx["is_frozen"] = self.object.is_frozen
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.is_frozen:
            return self._handle_frozen_post(request)
        return self._handle_editable_post(request)

    @transaction.atomic
    def _handle_frozen_post(self, request):
        form = OrderStatusForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, _("Order status updated."))
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))

    @transaction.atomic
    def _handle_editable_post(self, request):
        form = OrderForm(
            request.POST,
            instance=self.object,
            store=request.user.store,
            user=request.user,
        )
        formset = OrderItemFormSet(
            request.POST, instance=self.object, store=request.user.store
        )

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, _("Order updated successfully."))
            return HttpResponseRedirect(self.get_success_url())

        messages.error(request, _("Please correct the errors below."))
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


# ---------------------------------------------------------------------------
# Soft Delete View
# ---------------------------------------------------------------------------
class OrderSoftDeleteView(LoginRequiredMixin, StoreManagerRequiredMixin, DeleteView):
    """
    Soft-delete an Order. The actual stock restoration is handled safely by the Signals.
    """

    model = Order
    success_url = reverse_lazy("orders:order_list")

    def get_queryset(self):
        # Insurance: It only retrieves orders from this store that haven't been deleted.
        return Order.objects.filter(store=self.request.user.store, is_deleted=False)

    def form_valid(self, form):
        # `self.get_object()` retrieves the order from the queryset defined above.
        order = self.get_object()

        # Freezing Validation
        if order.is_frozen:
            messages.error(self.request, _("Cannot delete a frozen order."))
            return redirect(self.success_url)

        # 2. Status Change and Soft Delete (The magic happens here)
        # We don't need to iterate over the products at all! The signal will handle everything upon saving.
        order.status = Order.Status.CANCELLED
        order.is_deleted = True
        order.save()

        messages.success(self.request, _("Order deleted successfully."))
        return redirect(self.success_url)


# ---------------------------------------------------------------------------
# SHIPPER Available Orders View
# ---------------------------------------------------------------------------
class AvailableOrdersListView(
    LoginRequiredMixin, TenantQuerySetMixin, ShipperRequiredMixin, ListView
):
    """
    Shipper View: Lists all orders that are PREPARING and not assigned to anyone yet.
    """

    model = Order
    template_name = "orders/available_orders.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user

        # The orders are being prepared, but no courier has picked them up yet.
        qs = (
            super()
            .get_queryset()
            .filter(status=Order.Status.PREPARING, shipper__isnull=True)
        )

        return qs.select_related("customer").prefetch_related("items__product")


# ---------------------------------------------------------------------------
# SHIPPER Take Orders View
# ---------------------------------------------------------------------------
class TakeOrderView(LoginRequiredMixin, ShipperRequiredMixin, View):
    """
    Shipper Action: Assigns an available order to the current shipper
    and changes its status to SHIPPED.
    """

    def post(self, request, pk, *args, **kwargs):
        user = request.user

        # transaction.atomic + select_for_update:
        # (Race Condition Protection) Very robust protection in case two shippers click "Receive" at the exact same second.
        with transaction.atomic():
            # We retrieve the order and make sure it's still PREPARING and no one has taken it.
            order = get_object_or_404(
                Order.objects.select_for_update(),
                pk=pk,
                store=user.store,
                status=Order.Status.PREPARING,
                shipper__isnull=True,
            )

            # set the shipper
            order.shipper = user
            # We are changing the status to Shipped
            order.status = Order.Status.SHIPPED
            order.save(update_fields=["shipper", "status"])

        messages.success(
            request,
            _(
                "The order has been successfully received! It is now in your possession."
            ),
        )
        return redirect("orders:order_list")


# ---------------------------------------------------------------------------
# SHIPPER update Orders status only View
# ---------------------------------------------------------------------------
class ShipperOrderUpdateView(LoginRequiredMixin, TenantQuerySetMixin, ShipperRequiredMixin, UpdateView):
    """
    Dedicated UpdateView for Shippers.
    Separated from the Manager's view to keep code clean and maintain SRP.
    """

    model = Order
    form_class = ShipperOrderStatusForm
    template_name = "orders/shipper_order_form.html"
    success_url = reverse_lazy("orders:order_list")

    def get_queryset(self):
        return super().get_queryset().filter(shipper=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _("Delivery status updated successfully."))
        return super().form_valid(form)
