from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import gettext_lazy as _
from products.models import Product
from .models import Order, OrderItem, Customer

User = get_user_model()


class OrderForm(forms.ModelForm):
    """
    Form for creating/updating an Order.

    Rules:
    - The store is injected from the view and used to filter related querysets.
    - The user can either SELECT an existing Customer (filtered by store) OR
        provide `new_customer_name` + `new_customer_phone` to create one on the fly.
    """

    new_customer_name = forms.CharField(
        max_length=200,
        required=False,
        label=_("New Customer Name"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Enter new customer name")}
        ),
    )
    new_customer_phone = forms.CharField(
        max_length=20,
        required=False,
        label=_("New Customer Phone"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("+1234567890")}
        ),
    )

    class Meta:
        model = Order
        fields = ["customer", "status", "payment_method", "shipper", "notes"]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "shipper": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        # `store` and `user` are injected by the view via get_form_kwargs().
        self.store = kwargs.pop("store", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.store is not None:
            self.instance.store = self.store

            # Tenant isolation for Customer dropdown
            self.fields["customer"].queryset = Customer.objects.filter(
                store=self.store, is_deleted=False
            )
            self.fields["customer"].required = False  # can be created on the fly

            # Shipper dropdown: only SHIPPERs of the same store
            self.fields["shipper"].queryset = User.objects.filter(
                store=self.store, role=User.Role.SHIPPER, is_active=True
            )
            self.fields["shipper"].required = False

    def clean(self):
        cleaned = super().clean()
        customer = cleaned.get("customer")
        new_name = cleaned.get("new_customer_name")
        new_phone = cleaned.get("new_customer_phone")

        if not customer:
            # Must provide BOTH new fields if no existing customer is selected.
            if not (new_name and new_phone):
                raise ValidationError(
                    _(
                        "Please select an existing customer OR provide both a new name and phone number."
                    )
                )
        else:
            # Defensive: if a customer is selected, new_* fields should be blank.
            if new_name or new_phone:
                raise ValidationError(
                    _(
                        "Provide either an existing customer or new customer details — not both."
                    )
                )
        # Ensure the phone number is not duplicated when registering a new customer.
        if new_phone and self.store:
            phone_exists = Customer.objects.filter(
                store=self.store, phone_number=new_phone, is_deleted=False
            ).exists()

            if phone_exists:
                raise ValidationError(
                    {
                        "new_customer_phone": _(
                            "This number is already registered to another customer in your store. Please select it from the list."
                        )
                    }
                )

        return cleaned

    def save(self, commit=True):
        order = super().save(commit=False)

        # Enforce tenant ownership on the Order regardless of client input.
        if self.store is not None:
            order.store = self.store

        # Create the new Customer on the fly if needed.
        if not self.cleaned_data.get("customer"):
            new_name = self.cleaned_data["new_customer_name"]
            new_phone = self.cleaned_data["new_customer_phone"]
            customer = Customer.objects.create(
                store=self.store,
                name=new_name,
                phone_number=new_phone,
            )
            order.customer = customer

        if commit:
            order.save()
        return order


class OrderItemForm(forms.ModelForm):
    """Form for a single OrderItem inside the inline formset."""

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "step": 1}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.store = kwargs.pop("store", None)
        super().__init__(*args, **kwargs)

        if self.store is not None:
            self.instance.store = self.store

            # Tenant isolation: only show products of the current store.
            self.fields["product"].queryset = Product.objects.filter(
                store=self.store, is_active=True, is_deleted=False
            )
        else:
            self.fields["product"].queryset = Product.objects.none()


class BaseOrderItemFormSet(BaseInlineFormSet):
    """
    Custom base formset that propagates `store` from the view down to each
    OrderItemForm so product querysets stay tenant-scoped.
    """

    def __init__(self, *args, **kwargs):
        self.store = kwargs.pop("store", None)
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["store"] = self.store
        return kwargs


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    formset=BaseOrderItemFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class OrderStatusForm(forms.ModelForm):
    """
    Restricted form used when an Order is frozen (SHIPPED/DELIVERED/CANCELLED).
    Only `status` and `notes` may be edited; items are read-only.
    """

    class Meta:
        model = Order
        fields = ["status", "notes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ShipperOrderStatusForm(forms.ModelForm):
    """
    Restricted status update form used by Shippers (Delivery Workers).

    Business Rules:
    - Shippers can only set status to SHIPPED, DELIVERED, or RETURNED.
    - They may update the `notes` field for delivery-related comments.
    - They CANNOT modify items, customer, payment, or shipper assignment.
    """

    class Meta:
        model = Order
        fields = ["status", "notes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Restrict the status dropdown to only shipper-allowed transitions.
        allowed = {
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
            Order.Status.RETURNED,
        }
        self.fields["status"].choices = [
            (value, label) for value, label in Order.Status.choices if value in allowed
        ]

    def clean_status(self):
        """Defensive check: reject statuses outside the allowed set even if tampered with."""
        status = self.cleaned_data["status"]
        if status not in (
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
            Order.Status.RETURNED,
        ):
            raise forms.ValidationError(_("You are not allowed to set this status."))
        return status
