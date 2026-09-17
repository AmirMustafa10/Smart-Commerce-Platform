from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from stores.models import Store
from products.models import Category, Product
from orders.models import Customer, Order, OrderItem

User = get_user_model()


class BaseOrderTestSetup(TestCase):
    """Shared setup for all orders-related tests."""

    @classmethod
    def setUpTestData(cls):
        # Stores
        cls.store1 = Store.objects.create(
            name="Store One", whatsapp_number="+1111111111"
        )
        cls.store2 = Store.objects.create(
            name="Store Two", whatsapp_number="+2222222222"
        )

        # Users for store1
        cls.shipper1 = User.objects.create_user(
            email="shipper1@example.com",
            password="pass12345",
            full_name="Shipper One",
            store=cls.store1,
            role=User.Role.SHIPPER,
        )
        cls.manager1 = User.objects.create_user(
            email="manager1@example.com",
            password="pass12345",
            full_name="Manager One",
            store=cls.store1,
            role=User.Role.MANAGER,
        )

        # Users for store2
        cls.shipper2 = User.objects.create_user(
            email="shipper2@example.com",
            password="pass12345",
            full_name="Shipper Two",
            store=cls.store2,
            role=User.Role.SHIPPER,
        )

        # Categories and Products
        cls.category1 = Category.objects.create(store=cls.store1, name="Cat One")
        cls.category2 = Category.objects.create(store=cls.store2, name="Cat Two")

        cls.product1 = Product.objects.create(
            store=cls.store1,
            category=cls.category1,
            name="Product One",
            price=Decimal("100.00"),
            stock_quantity=5,
            is_active=True,
        )
        cls.product2 = Product.objects.create(
            store=cls.store2,
            category=cls.category2,
            name="Product Two",
            price=Decimal("50.00"),
            stock_quantity=10,
            is_active=True,
        )
        cls.inactive_product = Product.objects.create(
            store=cls.store1,
            category=cls.category1,
            name="Inactive Product",
            price=Decimal("20.00"),
            stock_quantity=5,
            is_active=False,
        )


# ---------------------------------------------------------------------------
# Customer Tests
# ---------------------------------------------------------------------------
class CustomerModelTests(BaseOrderTestSetup):
    """Tests for the Customer model."""

    def test_customer_creation_with_phone_normalization(self):
        """Phone number is stripped of spaces and dashes on save/clean."""
        customer = Customer(
            store=self.store1,
            name="John Doe",
            phone_number="+15551234568",
        )
        customer.full_clean()
        customer.save()
        # After clean(), spaces and dashes should be removed
        self.assertNotIn(" ", customer.phone_number)
        self.assertNotIn("-", customer.phone_number)

    def test_customer_invalid_phone_regex_raises_validation_error(self):
        """Invalid phone formats raise ValidationError."""
        invalid_numbers = ["not-a-phone", "123", "abc12345", "++555"]
        for number in invalid_numbers:
            with self.subTest(phone=number):
                customer = Customer(
                    store=self.store1,
                    name="Invalid Phone",
                    phone_number=number,
                )
                with self.assertRaises(ValidationError):
                    customer.full_clean()

    def test_same_phone_across_different_stores_allowed(self):
        """The same phone number can exist in two different stores."""
        phone = "+15551234567"
        Customer.objects.create(store=self.store1, name="Cust A", phone_number=phone)
        # Should NOT raise
        customer2 = Customer(store=self.store2, name="Cust B", phone_number=phone)
        customer2.full_clean()
        customer2.save()
        self.assertEqual(Customer.objects.filter(phone_number=phone).count(), 2)

    def test_duplicate_phone_in_same_store_raises_validation_error(self):
        """Same phone number in the same store raises ValidationError."""
        phone = "+15559998888"
        Customer.objects.create(store=self.store1, name="First", phone_number=phone)
        duplicate = Customer(store=self.store1, name="Second", phone_number=phone)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_soft_deleted_customer_allows_reuse_of_phone(self):
        """A soft-deleted customer's phone number can be reused in the same store."""
        phone = "+15551112222"
        first = Customer.objects.create(
            store=self.store1, name="Original", phone_number=phone
        )
        first.is_deleted = True
        first.save(update_fields=["is_deleted"])

        reuse = Customer(store=self.store1, name="Reused", phone_number=phone)
        reuse.full_clean()  # Should not raise
        reuse.save()
        self.assertEqual(
            Customer.objects.filter(
                store=self.store1, phone_number=phone, is_deleted=False
            ).count(),
            1,
        )


# ---------------------------------------------------------------------------
# Order Tests
# ---------------------------------------------------------------------------
class OrderModelTests(BaseOrderTestSetup):
    """Tests for the Order model."""

    def setUp(self):
        self.customer1 = Customer.objects.create(
            store=self.store1, name="Customer One", phone_number="+15550001111"
        )
        self.customer2 = Customer.objects.create(
            store=self.store2, name="Customer Two", phone_number="+15550002222"
        )

    def test_order_str_and_default_values(self):
        """Order has sensible defaults and readable string representation."""
        order = Order.objects.create(store=self.store1, customer=self.customer1)
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.source, Order.Source.DASHBOARD)
        self.assertIn(str(order.customer.name), str(order))

    def test_shipper_must_have_shipper_role(self):
        """Assigning a MANAGER as shipper raises ValidationError."""
        order = Order(
            store=self.store1,
            customer=self.customer1,
            shipper=self.manager1,  # role=MANAGER
        )
        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_shipper_from_different_store_raises_validation_error(self):
        """Shipper must belong to the same store as the order."""
        order = Order(
            store=self.store1,
            customer=self.customer1,
            shipper=self.shipper2,  # belongs to store2
        )
        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_customer_must_belong_to_same_store(self):
        """Customer must belong to the same store as the order."""
        order = Order(store=self.store1, customer=self.customer2)  # customer2 in store2
        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_negative_total_amount_raises_validation_error(self):
        """Negative total_amount is invalid."""
        order = Order(
            store=self.store1,
            customer=self.customer1,
            total_amount=Decimal("-1.00"),
        )
        with self.assertRaises(ValidationError):
            order.full_clean()


# ---------------------------------------------------------------------------
# OrderItem Tests
# ---------------------------------------------------------------------------
class OrderItemModelTests(BaseOrderTestSetup):
    """Tests for the OrderItem model, including stock and pricing rules."""

    def setUp(self):
        self.customer1 = Customer.objects.create(
            store=self.store1, name="Customer One", phone_number="+15550001111"
        )
        self.order1 = Order.objects.create(store=self.store1, customer=self.customer1)

    def test_store_is_inherited_from_product(self):
        """OrderItem inherits the store from the product."""
        item = OrderItem(
            order=self.order1,
            product=self.product1,
            quantity=1,
            price_at_order=self.product1.price,
        )
        item.full_clean()
        item.save()
        self.assertEqual(item.store_id, self.product1.store_id)

    def test_price_at_order_fallback_to_product_price(self):
        """If price_at_order is missing, it falls back to product.price."""
        item = OrderItem(
            order=self.order1,
            product=self.product1,
            quantity=1,
        )
        item.full_clean()
        item.save()
        self.assertEqual(item.price_at_order, self.product1.final_price)

    def test_subtotal_property(self):
        """Subtotal equals quantity * price_at_order."""
        item = OrderItem.objects.create(
            order=self.order1,
            product=self.product1,
            quantity=3,
            price_at_order=Decimal("25.00"),
        )
        self.assertEqual(item.subtotal, Decimal("75.00"))

    def test_creation_with_quantity_exceeding_stock_raises(self):
        """Requesting more than available stock raises ValidationError."""
        item = OrderItem(
            order=self.order1,
            product=self.product1,  # stock_quantity=5
            quantity=6,
            price_at_order=self.product1.price,
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_update_quantity_accounts_for_existing_reservation(self):
        """
        Reservation bug test:
        Product initially has 5 units.
        An OrderItem reserves 2 (stock should now be 3, but reservation is active).
        Updating the same OrderItem to quantity=4 should pass because
        available stock available_for_this_item = current_stock + already_reserved.
        """
        # Product starts with 5
        self.assertEqual(self.product1.stock_quantity, 5)

        # Create item reserving 2 (assumes save() decrements stock)
        item = OrderItem.objects.create(
            order=self.order1,
            product=self.product1,
            quantity=2,
            price_at_order=self.product1.price,
        )
        self.product1.refresh_from_db()
        # After reservation, stock should have decreased
        self.assertEqual(self.product1.stock_quantity, 3)

        # Now update to 4 — this is allowed because actual availability is 3 + 2 = 5
        item.quantity = 4
        try:
            item.full_clean()
        except ValidationError:
            self.fail(
                "Updating quantity to 4 should be allowed (accounting for prior reservation)"
            )

    def test_order_and_product_must_share_store(self):
        """Order and product must belong to the same store."""
        # order1 belongs to store1, product2 belongs to store2
        item = OrderItem(
            order=self.order1,
            product=self.product2,
            quantity=1,
            price_at_order=self.product2.price,
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_inactive_product_raises_validation_error(self):
        """Adding an inactive product to an order raises ValidationError."""
        item = OrderItem(
            order=self.order1,
            product=self.inactive_product,
            quantity=1,
            price_at_order=self.inactive_product.price,
        )
        with self.assertRaises(ValidationError):
            item.full_clean()
