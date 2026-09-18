import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TenantAwareModel
from products.models import Product


class Customer(TenantAwareModel):
    """Customer belonging to a specific store (tenant)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(_("name"), max_length=200)
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^\+[1-9]\d{8,14}$",
                message=_(
                    "Phone number must be in international format (e.g., +14155552671)."
                ),
            )
        ],
        help_text=_("Customer's contact phone number (unique per store)."),
    )
    address = models.TextField(_("address"), blank=True, default="")

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["store", "phone_number"]),
            models.Index(fields=["store", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    def clean_fields(self, exclude=None):
        """Data cleaning/processing prior to validation (Regex)"""

        if self.name:
            self.name = self.name.strip()

        if self.phone_number:
            self.phone_number = (
                self.phone_number.strip().replace(" ", "").replace("-", "")
            )

        super().clean_fields(exclude=exclude)

    def clean(self):
        """Validate uniqueness of phone_number per store (ignoring soft-deleted)."""
        super().clean()

        if self.store_id and self.phone_number:
            duplicate = (
                Customer.objects.filter(
                    store_id=self.store_id,
                    phone_number=self.phone_number,
                    is_deleted=False,
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if duplicate:
                raise ValidationError(
                    {
                        "phone_number": _(
                            "A customer with this phone number already exists in this store."
                        )
                    }
                )


class Order(TenantAwareModel):
    """Order placed by a customer, optionally assigned to a shipper."""

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        CONFIRMED = "CONFIRMED", _("Confirmed")
        PREPARING = "PREPARING", _("Preparing")
        SHIPPED = "SHIPPED", _("Shipped")
        DELIVERED = "DELIVERED", _("Delivered")
        CANCELLED = "CANCELLED", _("Cancelled")
        RETURNED = "RETURNED", _("Returned")

    class Source(models.TextChoices):
        DASHBOARD = "DASHBOARD", _("Dashboard (Manual Entry)")
        WHATSAPP_AI = "WHATSAPP_AI", _("WhatsApp AI Bot")

    class PaymentMethod(models.TextChoices):
        COD = "COD", _("Cash on Delivery")
        CREDIT_CARD = "CREDIT_CARD", _("Credit Card (Online)")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    shipper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
        limit_choices_to={"role": "SHIPPER"},
        help_text=_("Shipper assigned to deliver this order (role must be SHIPPER)."),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    source = models.CharField(
        _("source"),
        max_length=20,
        choices=Source.choices,
        default=Source.DASHBOARD,
        help_text=_("Where the order originated from."),
    )
    payment_method = models.CharField(
        _("payment method"),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
    )
    is_paid = models.BooleanField(
        _("is paid"),
        default=False,
        help_text=_("True if the customer has paid for this order."),
    )
    total_amount = models.DecimalField(
        _("total amount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    notes = models.TextField(_("notes"), blank=True, default="")
    delivered_at = models.DateTimeField(null=True, blank=True)
    is_settled = models.BooleanField(
        default=False, verbose_name="The cash has been deposited."
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["store", "status"]),
            models.Index(fields=["store", "source"]),
            models.Index(fields=["store", "is_deleted"]),
        ]

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"

    def clean(self):
        """Validate tenant isolation and business rules."""
        super().clean()

        if self.total_amount is not None and self.total_amount < Decimal("0.00"):
            raise ValidationError(
                {"total_amount": _("Total amount cannot be negative.")}
            )

        # Condition: If the status is "Delivered" and there is no "SHIPPED"
        if (
            self.status in [self.Status.DELIVERED, self.Status.SHIPPED]
            and not self.shipper
        ):
            raise ValidationError(
                {
                    "status": _(
                        'The order cannot be changed to "Delivered" without assigning a SHIPPER.'
                    ),
                    "shipper": _("Please assign a Shipper first."),
                }
            )

        # Customer must belong to the same store
        if self.customer_id and self.store_id:
            if self.customer.store_id != self.store_id:
                raise ValidationError(
                    {"customer": _("Selected customer does not belong to this store.")}
                )

        # Shipper must belong to the same store and have role=SHIPPER
        if self.shipper_id and self.store_id:
            shipper = self.shipper
            if shipper.store_id != self.store_id:
                raise ValidationError(
                    {"shipper": _("Selected shipper does not belong to this store.")}
                )
            if shipper.role != "SHIPPER":
                raise ValidationError({"shipper": _("Selected user is not a shipper.")})

        # Prevent reviving dead (cancelled or deleted) orders
        if not self._state.adding and self.pk:
            try:
                old_order = type(self).all_objects.get(
                    pk=self.pk
                )  # We used `all_objects` to retrieve the hidden order.

                # Prohibit Soft Delete Reversal
                if old_order.is_deleted and not self.is_deleted:
                    raise ValidationError(
                        {
                            "is_deleted": "A deleted order cannot be recovered. Create a new order (Reorder)."
                        }
                    )

                # Prevent activation of a cancelled or returned order.
                inactive_statuses = [self.Status.CANCELLED, self.Status.RETURNED]
                if (
                    old_order.status in inactive_statuses
                    and self.status not in inactive_statuses
                ):
                    raise ValidationError(
                        {
                            "status": "A cancelled or returned order cannot be reactivated. Please create a new order (Reorder)."
                        }
                    )
            except type(self).DoesNotExist:
                pass

        def save(self, *args, **kwargs):
            self.full_clean()
            super().save(*args, **kwargs)

    @property
    def is_frozen(self):
        """Returns True if the order is in a state where items cannot be modified."""
        frozen_statuses = [
            self.Status.SHIPPED,
            self.Status.DELIVERED,
            self.Status.CANCELLED,
            self.Status.RETURNED,
        ]
        return self.status in frozen_statuses


class OrderItem(TenantAwareModel):
    """Line item of an order, preserving the price at the time of purchase."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    price_at_order = models.DecimalField(
        _("price at order"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Snapshot of the product price at the time of purchase."),
    )

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")
        ordering = ["id"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["store", "is_deleted"]),
        ]

    def __str__(self):
        if getattr(self, "product_id", None):
            return f"{self.quantity} x {self.product.name} (Order {self.order_id})"
        return "New Order Item"

    def clean_fields(self, exclude=None):
        """Automatically fetch the price before Django performs validation."""
        if getattr(self, "product_id", None):
            if self.price_at_order is None:
                self.price_at_order = self.product.final_price

            # Inheriting the store from the producer
            self.store_id = self.product.store_id

        super().clean_fields(exclude=exclude)

    def clean(self):
        """Validate tenant isolation, quantity, and pricing snapshot."""

        super().clean()

        if getattr(self, "order_id", None):
            frozen_statuses = [
                Order.Status.SHIPPED,
                Order.Status.CANCELLED,
                Order.Status.RETURNED,
                Order.Status.DELIVERED,
            ]
            if self.order.status in frozen_statuses:
                if self._state.adding:
                    raise ValidationError(
                        {
                            "__all__": f"Products cannot be modified or added to an order with the status '{self.order.get_status_display()}'."
                        }
                    )
                elif self.pk:
                    try:
                        old_item = type(self).objects.get(pk=self.pk)
                        # We compare the old with the new; if there’s a change, we throw an error.
                        if (
                            old_item.product_id != getattr(self, "product_id", None)
                            or old_item.quantity != self.quantity
                        ):
                            raise ValidationError(
                                {
                                    "__all__": f"Order products cannot be modified for an order with the status '{self.order.get_status_display()}'."
                                }
                            )
                    except type(self).DoesNotExist:
                        pass

        # Verifying the reasonableness of the figures
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError(
                {"quantity": _("Quantity must be greater than zero.")}
            )

        if self.price_at_order is not None and self.price_at_order < Decimal("0.00"):
            raise ValidationError(
                {"price_at_order": _("Price at order cannot be negative.")}
            )

        if getattr(self, "product_id", None):
            if not self.product.is_active:
                raise ValidationError(
                    {
                        "product": f"Sorry, the product '{self.product.name}' is currently not available for sale."
                    }
                )

            actual_available_stock = self.product.stock_quantity

            # If this is a modification to a previously registered product (not a new one), we add its old quantity to the inventory.
            if not self._state.adding and self.pk:
                try:
                    old_item = type(self).objects.get(pk=self.pk)
                    actual_available_stock += old_item.quantity
                except type(self).DoesNotExist:
                    pass

            # Is the required quantity available in stock?
            if self.quantity > actual_available_stock:
                raise ValidationError(
                    {
                        "quantity": f"The requested quantity ({self.quantity}) exceeds the available stock ({actual_available_stock}) for the product '{self.product.name}'."
                    }
                )

        # Verify that the order belongs to the same store as the product.
        if getattr(self, "order_id", None) and getattr(self, "store_id", None):
            if self.order.store_id != self.store_id:
                raise ValidationError(
                    {"__all__": _("Selected item does not belong to this store.")}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.quantity * self.price_at_order
