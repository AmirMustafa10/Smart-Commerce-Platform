# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Customer, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for the Customer model."""

    list_display = ("name", "phone_number", "store", "created_at")
    list_filter = ("store", "created_at")
    search_fields = ("name", "phone_number")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)

    # Grouped fieldsets for a cleaner edit page
    fieldsets = (
        (_("Basic Info"), {"fields": ("id", "store", "name", "phone_number")}),
        (_("Address"), {"fields": ("address",)}),
        (_("Status"), {"fields": ("is_deleted",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


class OrderItemInline(admin.TabularInline):
    """
    Inline representation of OrderItem inside the Order admin.
    Displays product, quantity, price snapshot, and a computed subtotal.
    """

    model = OrderItem
    extra = 0

    def has_delete_permission(self, request, obj=None):
        """
        Hide the delete button for products if the order is closed.
        (Here, `obj` refers to the order itself.)
        """

        if obj:
            frozen_statuses = [
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
                Order.Status.CANCELLED,
                Order.Status.RETURNED,
            ]
            if obj.status in frozen_statuses:
                return False
        return True

    fields = ("product", "quantity", "get_subtotal")
    readonly_fields = ("get_subtotal",)
    autocomplete_fields = ("product",)

    @admin.display(description=_("Subtotal"))
    def get_subtotal(self, obj):
        """Calculate and display the subtotal for this order item."""
        if obj.quantity is None or obj.price_at_order is None:
            return "—"
        subtotal = obj.quantity * obj.price_at_order
        return format_html("<strong>{}</strong>", f"{subtotal:.2f}")


@admin.action(description=_("Soft Delete selected orders (Cancel & Hide)"))
def soft_delete_orders(modeladmin, request, queryset):
    """
    A custom action that performs a soft delete on selected orders.
    It changes their status to "Cancelled" so that inventory is returned, and then hides them.
    """

    for order in queryset:
        # If the order is active, we cancel it first so the signal returns the goods.
        active_statuses = [
            Order.Status.PENDING,
            Order.Status.CONFIRMED,
            Order.Status.PREPARING,
        ]
        if order.status in active_statuses:
            order.status = Order.Status.CANCELLED

        # We perform a soft delete on it.
        order.is_deleted = True

        # We use save() instead of update() so that the signals work.
        order.save()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model."""

    list_display = (
        "store",
        "customer",
        "shipper__full_name",
        "status",
        "source",
        "total_amount",
        "payment_method",
        "created_at",
    )
    list_filter = ("status", "source", "store", "created_at", "delivered_at", "payment_method")
    search_fields = ("customer__name", "customer__phone_number", "id")
    readonly_fields = ("id", "total_amount", "created_at", "updated_at", "delivered_at")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)

    # Autocomplete for large datasets: requires search_fields on the related admins.
    autocomplete_fields = ("customer", "shipper")

    fieldsets = (
        (_("Basic Info"), {"fields": ("id", "store", "customer", "shipper", "payment_method")}),
        (_("Order Details"), {"fields": ("status", "source", "total_amount", "is_settled")}),
        (_("Notes"), {"fields": ("notes",)}),
        (_("Status"), {"fields": ("is_deleted",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at", "delivered_at")}),
    )

    actions = [soft_delete_orders]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Standalone admin for OrderItem (optional), useful for auditing.
    OrderItem is primarily managed as an inline of Order.
    """

    list_display = ("id", "order", "product", "quantity", "store")
    list_filter = ("store", "created_at")
    search_fields = ("order__id", "product__name")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "price_at_order",
    )
    autocomplete_fields = ("order", "product")
    ordering = ("-created_at",)
