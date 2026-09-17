from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from stores.models import Store
from products.models import Category, Product
from orders.models import Customer, Order
from orders.forms import OrderForm, ShipperOrderStatusForm

User = get_user_model()


class OrdersFormTestBase(TestCase):
    """Shared fixture for form tests."""

    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(
            name="Main Store", whatsapp_number="+12025550100"
        )
        cls.other_store = Store.objects.create(
            name="Other Store", whatsapp_number="+12025550200"
        )

        cls.manager = User.objects.create_user(
            email="manager@example.com",
            password="pass12345",
            full_name="Manager",
            store=cls.store,
            role=User.Role.MANAGER,
        )
        cls.shipper = User.objects.create_user(
            email="shipper@example.com",
            password="pass12345",
            full_name="Shipper",
            store=cls.store,
            role=User.Role.SHIPPER,
        )

        cls.customer = Customer.objects.create(
            store=cls.store, name="Alice Buyer", phone_number="+12025550199"
        )
        cls.category = Category.objects.create(store=cls.store, name="General")
        cls.product = Product.objects.create(
            store=cls.store,
            category=cls.category,
            name="Widget",
            price=Decimal("10.00"),
            stock_quantity=500,
            is_active=True,
        )

        cls.order = Order.objects.create(
            store=cls.store,
            customer=cls.customer,
            status=Order.Status.SHIPPED,
            payment_method=Order.PaymentMethod.COD,
            shipper=cls.shipper,
        )


class TestOrderForm(OrdersFormTestBase):
    """Validation tests for OrderForm."""

    def _base_data(self, **overrides):
        """Helper: build a valid baseline payload, then apply overrides."""
        data = {
            "customer": "",
            "status": Order.Status.PENDING,
            "payment_method": Order.PaymentMethod.COD,
            "shipper": "",
            "notes": "",
            "new_customer_name": "",
            "new_customer_phone": "",
        }
        data.update(overrides)
        return data

    def test_valid_with_existing_customer(self):
        """OrderForm accepts an existing customer and no new-customer fields."""
        form = OrderForm(
            data=self._base_data(customer=self.customer.pk),
            store=self.store,
            user=self.manager,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_with_new_customer_fields(self):
        """OrderForm accepts new-customer fields and no existing customer."""
        form = OrderForm(
            data=self._base_data(
                new_customer_name="New Buyer",
                new_customer_phone="+12025550777",
            ),
            store=self.store,
            user=self.manager,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_when_both_customer_and_new_fields(self):
        """XOR rule: providing BOTH existing customer and new fields is invalid."""
        form = OrderForm(
            data=self._base_data(
                customer=self.customer.pk,
                new_customer_name="Conflicting",
                new_customer_phone="+12025550888",
            ),
            store=self.store,
            user=self.manager,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_invalid_when_neither_customer_nor_new_fields(self):
        """XOR rule: providing NEITHER customer nor new fields is invalid."""
        form = OrderForm(
            data=self._base_data(),
            store=self.store,
            user=self.manager,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_duplicate_phone_in_same_store_is_rejected(self):
        """
        A new customer created via OrderForm cannot reuse an existing
        phone number within the same store. Failure must surface either
        at form validation or during Customer.save().
        """
        form = OrderForm(
            data=self._base_data(
                new_customer_name="Dup Buyer",
                new_customer_phone=self.customer.phone_number,
            ),
            store=self.store,
            user=self.manager,
        )
        if form.is_valid():
            with self.assertRaises(ValidationError):
                form.save()
        else:
            self.assertIn("new_customer_phone", form.errors)

    def test_customer_dropdown_scoped_to_store(self):
        """Only customers of the injected store appear in the queryset."""
        other_customer = Customer.objects.create(
            store=self.other_store, name="Other Buyer", phone_number="+12025550333"
        )
        form = OrderForm(store=self.store, user=self.manager)
        qs = form.fields["customer"].queryset
        self.assertIn(self.customer, qs)
        self.assertNotIn(other_customer, qs)


class TestShipperOrderStatusForm(OrdersFormTestBase):
    """Validation tests for ShipperOrderStatusForm."""

    def test_allowed_choices_are_whitelisted(self):
        """Form only exposes SHIPPED, DELIVERED, RETURNED as status choices."""
        form = ShipperOrderStatusForm()
        values = [v for v, _ in form.fields["status"].choices]
        self.assertCountEqual(
            values,
            [Order.Status.SHIPPED, Order.Status.DELIVERED, Order.Status.RETURNED],
        )

    def test_accepts_valid_delivered_status(self):
        """DELIVERED is an allowed status."""
        form = ShipperOrderStatusForm(
            instance=self.order,
            data={"status": Order.Status.DELIVERED, "notes": "Dropped off."},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_tampered_status_cancelled(self):
        """A tampered POST with CANCELLED must be rejected by clean_status()."""
        form = ShipperOrderStatusForm(
            instance=self.order,
            data={"status": Order.Status.CANCELLED, "notes": "Dropped off."},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)

    def test_rejects_tampered_status_pending(self):
        """PENDING is not a shipper-allowed status."""
        form = ShipperOrderStatusForm(
            instance=self.order,
            data={"status": Order.Status.PENDING, "notes": "Dropped off."},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)
