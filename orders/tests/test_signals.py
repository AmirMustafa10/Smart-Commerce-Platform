from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from stores.models import Store
from products.models import Category, Product
from orders.models import Customer, Order, OrderItem
from django.core.exceptions import ValidationError

User = get_user_model()


class OrderTotalSignalTests(TestCase):
    """
    Tests for the `update_order_total` signal (post_save, post_delete on OrderItem).
    Verifies that Order.total_amount always reflects the sum of its items.
    """

    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(
            name="Signal Store", whatsapp_number="+1234567890"
        )
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass12345",
            full_name="Owner",
            store=cls.store,
            role=User.Role.OWNER,
        )
        cls.customer = Customer.objects.create(
            store=cls.store, name="Signal Customer", phone_number="+15550001111"
        )
        cls.category = Category.objects.create(store=cls.store, name="Signal Cat")
        cls.product_a = Product.objects.create(
            store=cls.store,
            category=cls.category,
            name="Product A",
            price=Decimal("100.00"),
            stock_quantity=100,
            is_active=True,
        )
        cls.product_b = Product.objects.create(
            store=cls.store,
            category=cls.category,
            name="Product B",
            price=Decimal("50.00"),
            stock_quantity=100,
            is_active=True,
        )

    def setUp(self):
        # Fresh Order for every test (setUpTestData is class-level and shared).
        self.order = Order.objects.create(store=self.store, customer=self.customer)

    def test_total_updates_on_item_creation(self):
        """Adding OrderItems updates order.total_amount incrementally."""
        OrderItem.objects.create(
            order=self.order,
            product=self.product_a,
            quantity=2,
            price_at_order=Decimal("100.00"),
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal("200.00"))

        OrderItem.objects.create(
            order=self.order,
            product=self.product_b,
            quantity=1,
            price_at_order=Decimal("50.00"),
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal("250.00"))

    def test_total_updates_on_item_deletion(self):
        """Deleting OrderItems decreases order.total_amount accordingly."""
        item_a = OrderItem.objects.create(
            order=self.order,
            product=self.product_a,
            quantity=2,
            price_at_order=Decimal("100.00"),
        )
        item_b = OrderItem.objects.create(
            order=self.order,
            product=self.product_b,
            quantity=1,
            price_at_order=Decimal("50.00"),
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal("250.00"))

        # Delete item A (200.00) -> expected 50.00
        item_a.delete()
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal("50.00"))

        # Delete item B (50.00) -> expected 0.00
        item_b.delete()
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal("0.00"))


class StockManagementSignalTests(TestCase):
    """
    Tests for stock signals:
      - deduct_stock_on_create (post_save)
      - adjust_stock_on_update (pre_save)
      - restore_stock_on_delete (post_delete)
    NOTE: Because signals use `.update()` with F() expressions, we MUST call
    refresh_from_db() before asserting on stock_quantity.
    """

    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(
            name="Stock Store", whatsapp_number="+1987654321"
        )
        cls.owner = User.objects.create_user(
            email="stock_owner@example.com",
            password="pass12345",
            full_name="Stock Owner",
            store=cls.store,
            role=User.Role.OWNER,
        )
        cls.customer = Customer.objects.create(
            store=cls.store, name="Stock Customer", phone_number="+15550002222"
        )
        cls.category = Category.objects.create(store=cls.store, name="Stock Cat")

    def setUp(self):
        # Each test gets a fresh product with stock_quantity=10.
        self.product = Product.objects.create(
            store=self.store,
            category=self.category,
            name="Stock Product",
            price=Decimal("25.00"),
            stock_quantity=10,
            is_active=True,
        )
        self.order = Order.objects.create(store=self.store, customer=self.customer)

    def test_stock_deducted_on_item_creation(self):
        """Creating an OrderItem deducts its quantity from product stock."""
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price_at_order=Decimal("25.00"),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)

    def test_stock_adjusted_when_quantity_increases(self):
        """Increasing quantity by 2 deducts 2 more from stock (3 → 5)."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price_at_order=Decimal("25.00"),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)

        item.quantity = 5
        item.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)

    def test_stock_adjusted_when_quantity_decreases(self):
        """Decreasing quantity by 4 restores 4 units (5 → 1)."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=5,
            price_at_order=Decimal("25.00"),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)

        item.quantity = 1
        item.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 9)

    def test_stock_restored_on_item_deletion(self):
        """Deleting an OrderItem restores its quantity back to stock."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price_at_order=Decimal("25.00"),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)

        item.delete()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)

    def test_full_stock_cycle(self):
        """
        End-to-end sanity check: create → increase → decrease → delete
        should leave stock back at the original value (10).
        """
        # Create (qty 3) -> stock 7
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price_at_order=Decimal("25.00"),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)

        # Increase to 5 -> stock 5
        item.quantity = 5
        item.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)

        # Decrease to 1 -> stock 9
        item.quantity = 1
        item.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 9)

        # Delete -> stock 10
        item.delete()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)


class OrderBusinessRulesTests(TestCase):
    def setUp(self):
        # Creating the store and the user
        self.store = Store.objects.create(
            name="Test Store", whatsapp_number="+21515856258"
        )
        self.user = User.objects.create_user(
            full_name="manager test",
            email="manager@yahoo.com",
            password="password",
            role=User.Role.MANAGER,
            store=self.store,
        )

        self.shipper = User.objects.create_user(
            email="shipper@example.com",
            password="pass12345",
            full_name="shipper",
            store=self.store,
            role=User.Role.SHIPPER,
        )

        # Creating the customer
        self.customer = Customer.objects.create(
            store=self.store, name="Test Customer", phone_number="+201000000000"
        )

        self.category = Category.objects.create(store=self.store, name="Signal Cat2")

        # Create a product with 10 inventory
        self.product = Product.objects.create(
            store=self.store,
            category=self.category,
            name="Test Product",
            price=Decimal("100.00"),
            stock_quantity=10,
            is_active=True,
        )

        # Create an order (default status: PENDING)
        self.order = Order.objects.create(
            store=self.store, customer=self.customer, source=Order.Source.DASHBOARD
        )

        # Adding an item to the order (here, the old signal will deduct 2 units from the inventory).
        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2
        )

        # Verify that the 2 items were deducted from the inventory, leaving a balance of 8 (so we can base the remaining tests on this).
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

    # ==========================================
    # Signal Tests: Order Status Monitoring
    # ==========================================

    def test_order_cancellation_restores_stock(self):
        """When an order is cancelled, the quantities must be returned to the warehouse."""

        self.order.status = Order.Status.CANCELLED
        self.order.save()

        # Updating the product from the database due to the use of `F()` and `.update()` within the signal.
        self.product.refresh_from_db()

        # The warehouse had 8, and the order was cancelled (its quantity was 2), it should be returned as 10.
        self.assertEqual(self.product.stock_quantity, 10)

    def test_order_reactivation_is_blocked(self):
        """Reactivating a cancelled or returned order must raise a ValidationError."""
        self.order.status = Order.Status.RETURNED
        self.order.save()

        # Attempt to reactivate
        self.order.status = Order.Status.PENDING
        with self.assertRaises(ValidationError) as context:
            self.order.full_clean()

        self.assertIn("status", context.exception.message_dict)

    def test_active_to_active_status_change_ignores_stock(self):
        """Changing the status between active states (e.g., from PENDING to SHIPPED) does not affect inventory."""

        self.order.status = Order.Status.SHIPPED
        self.order.shipper = self.shipper
        self.order.save()

        self.product.refresh_from_db()
        # The inventory remains at 8 (it is not deducted twice).
        self.assertEqual(self.product.stock_quantity, 8)

    # ==========================================
    # Validation Tests for Closed Orders
    # ==========================================

    def test_cannot_add_item_to_closed_order(self):
        """A new product cannot be added to an order with a "Closed" (Delivered) status."""

        self.order.status = Order.Status.DELIVERED
        self.order.shipper = self.shipper
        self.order.save()

        new_item = OrderItem(order=self.order, product=self.product, quantity=1)

        with self.assertRaises(ValidationError) as context:
            new_item.full_clean()

        # Verify that the error originated from `__all__`, just as we defined it in the module.
        self.assertIn("__all__", context.exception.message_dict)

    def test_cannot_update_item_in_closed_order(self):
        """The quantity of a product in a cancelled order cannot be modified."""

        self.order.status = Order.Status.CANCELLED
        self.order.save()

        # Attempting to modify the quantity of the old item.
        self.order_item.quantity = 5

        with self.assertRaises(ValidationError) as context:
            self.order_item.full_clean()

        self.assertIn("__all__", context.exception.message_dict)

    def test_cannot_delete_item_in_closed_order(self):
        """A product included in a closed order cannot be deleted."""

        # Change the order status to "Closed" (e.g., "SHIPPED").
        self.order.status = Order.Status.SHIPPED
        self.order.shipper = self.shipper
        self.order.save()

        # Attempting to actually delete the item (and verifying that the signal stops the process and raises an error).
        with self.assertRaises(ValidationError) as context:
            self.order_item.delete()

        # Verify that the error message that appeared is indeed related to our signal.
        self.assertIn("Products cannot be deleted", str(context.exception))

    # ==========================================
    # NEW: Tests for Order Soft Delete (is_deleted)
    # ==========================================

    def test_order_soft_delete_restores_stock(self):
        """When an order is soft-deleted, the goods must be restocked (even if status is still PENDING)."""
        self.order.is_deleted = True
        self.order.save()

        self.product.refresh_from_db()
        # Warehouse had 8. Soft-deleting should return the 2 items, making it 10.
        self.assertEqual(self.product.stock_quantity, 10)

    def test_order_soft_undelete_is_blocked(self):
        """Undeleting a soft-deleted order must raise a ValidationError."""
        self.order.is_deleted = True
        self.order.save()

        # Attempt to undelete
        self.order.is_deleted = False
        with self.assertRaises(ValidationError) as context:
            self.order.full_clean()

        self.assertIn("is_deleted", context.exception.message_dict)
