from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from stores.models import Store
from products.models import Category, Product
from orders.models import Customer, Order

User = get_user_model()


class OrdersViewTestBase(TestCase):
    """Shared fixture for view tests."""

    @classmethod
    def setUpTestData(cls):
        # ----- Stores -----
        cls.store = Store.objects.create(
            name="Main Store", whatsapp_number="+12025550100"
        )
        cls.other_store = Store.objects.create(
            name="Other Store", whatsapp_number="+12025550200"
        )

        # ----- Users -----
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass12345",
            full_name="Owner",
            store=cls.store,
            role=User.Role.OWNER,
        )
        cls.manager = User.objects.create_user(
            email="manager@example.com",
            password="pass12345",
            full_name="Manager",
            store=cls.store,
            role=User.Role.MANAGER,
        )
        cls.shipper_a = User.objects.create_user(
            email="shipper_a@example.com",
            password="pass12345",
            full_name="Shipper A",
            store=cls.store,
            role=User.Role.SHIPPER,
        )
        cls.shipper_b = User.objects.create_user(
            email="shipper_b@example.com",
            password="pass12345",
            full_name="Shipper B",
            store=cls.store,
            role=User.Role.SHIPPER,
        )
        cls.outsider_owner = User.objects.create_user(
            email="outsider@example.com",
            password="pass12345",
            full_name="Outsider",
            store=cls.other_store,
            role=User.Role.OWNER,
        )

        # ----- Business entities -----
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

        # ----- Orders -----
        cls.order_a = Order.objects.create(
            store=cls.store,
            customer=cls.customer,
            shipper=cls.shipper_a,
            status=Order.Status.SHIPPED,
        )
        cls.order_b = Order.objects.create(
            store=cls.store,
            customer=cls.customer,
            shipper=cls.shipper_b,
            status=Order.Status.SHIPPED,
        )
        cls.order_c = Order.objects.create(
            store=cls.store,
            customer=cls.customer,
            shipper=None,
            status=Order.Status.PREPARING,
        )

    def login(self, user):
        self.client.login(email=user.email, password="pass12345")


# ===========================================================================
# Manager / Owner Views
# ===========================================================================
class TestManagerOrderViews(OrdersViewTestBase):
    """View behaviour for OWNER / MANAGER roles."""

    def setUp(self):
        self.login(self.manager)

    # ---------- List ----------
    def test_manager_sees_only_own_store_orders(self):
        """OrderListView scopes results to the manager's store."""
        other_customer = Customer.objects.create(
            store=self.other_store, name="Other Buyer", phone_number="+12025550333"
        )
        other_order = Order.objects.create(
            store=self.other_store,
            customer=other_customer,
            status=Order.Status.PENDING,
        )

        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 200)

        orders = list(response.context["orders"])
        self.assertIn(self.order_a, orders)
        self.assertNotIn(other_order, orders)

    def test_manager_status_filter_deleted(self):
        """`?status=DELETED` surfaces soft-deleted orders to managers only."""
        self.order_a.is_deleted = True
        self.order_a.save(update_fields=["is_deleted"])

        response = self.client.get(reverse("orders:order_list"), {"status": "DELETED"})
        self.assertEqual(response.status_code, 200)

        orders = list(response.context["orders"])
        self.assertIn(self.order_a, orders)
        self.assertNotIn(self.order_c, orders)  # active order excluded

    # ---------- Create ----------
    def test_order_create_atomic_with_items(self):
        """POST to OrderCreateView creates the order AND items atomically."""
        url = reverse("orders:order_create")
        data = {
            "customer": self.customer.pk,
            "status": Order.Status.PENDING,
            "payment_method": Order.PaymentMethod.COD,
            "shipper": "",
            "notes": "First order",
            "new_customer_name": "",
            "new_customer_phone": "",
            # Inline formset management form
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "1",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": self.product.pk,
            "items-0-quantity": "3",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        new_order = Order.objects.filter(notes="First order").first()
        self.assertIsNotNone(new_order)
        self.assertEqual(new_order.store, self.store)
        self.assertEqual(new_order.items.count(), 1)
        self.assertEqual(new_order.items.first().quantity, 3)

    def test_order_create_rejects_empty_formset(self):
        """Formset with zero items must not create an Order."""
        url = reverse("orders:order_create")
        data = {
            "customer": self.customer.pk,
            "status": Order.Status.PENDING,
            "payment_method": Order.PaymentMethod.COD,
            "shipper": "",
            "notes": "Should fail",
            "new_customer_name": "",
            "new_customer_phone": "",
            "items-TOTAL_FORMS": "0",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "1",
            "items-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # re-rendered with errors
        self.assertFalse(Order.objects.filter(notes="Should fail").exists())

    # ---------- Update: frozen vs editable ----------
    def test_frozen_order_uses_status_only_form(self):
        """SHIPPED order → view uses OrderStatusForm, no live formset."""
        url = reverse("orders:order_update", kwargs={"pk": self.order_a.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get("is_frozen"))
        self.assertIsNone(response.context.get("formset"))

    def test_active_order_uses_full_form_and_formset(self):
        """PREPARING order → full OrderForm + formset."""
        url = reverse("orders:order_update", kwargs={"pk": self.order_c.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get("is_frozen"))
        self.assertIsNotNone(response.context.get("formset"))

    def test_frozen_order_post_updates_only_status(self):
        """POST to a frozen order updates status only, leaves items untouched."""
        url = reverse("orders:order_update", kwargs={"pk": self.order_a.pk})
        response = self.client.post(
            url, {"status": Order.Status.DELIVERED, "notes": "Done."}
        )
        self.assertRedirects(response, reverse("orders:order_list"))

        self.order_a.refresh_from_db()
        self.assertEqual(self.order_a.status, Order.Status.DELIVERED)
        self.assertEqual(self.order_a.notes, "Done.")

    # ---------- Soft delete ----------
    def test_soft_delete_sets_flag_and_cancelled_status(self):
        """OrderSoftDeleteView marks is_deleted=True and status=CANCELLED."""
        url = reverse("orders:order_delete", kwargs={"pk": self.order_c.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("orders:order_list"))

        self.order_c.refresh_from_db()
        self.assertTrue(self.order_c.is_deleted)
        self.assertEqual(self.order_c.status, Order.Status.CANCELLED)

    def test_frozen_order_cannot_be_soft_deleted(self):
        """A frozen (SHIPPED) order must NOT be deletable."""
        url = reverse("orders:order_delete", kwargs={"pk": self.order_a.pk})
        self.client.post(url)

        self.order_a.refresh_from_db()
        self.assertFalse(self.order_a.is_deleted)
        self.assertEqual(self.order_a.status, Order.Status.SHIPPED)

    # ---------- RBAC & Tenant Isolation ----------
    def test_outsider_manager_cannot_access_other_store_order(self):
        """A manager from another store must get 404 on this store's orders."""
        self.login(self.outsider_owner)
        url = reverse("orders:order_update", kwargs={"pk": self.order_a.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_redirected_to_login(self):
        """Anonymous users are redirected to the login page."""
        self.client.logout()
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


# ===========================================================================
# Shipper Views
# ===========================================================================
class TestShipperOrderViews(OrdersViewTestBase):
    """Assignment isolation and workflow tests for SHIPPER role."""

    # ---------- Assigned-orders list ----------
    def test_shipper_list_only_returns_own_orders(self):
        """Shipper A sees Order A only; never Order B."""
        self.login(self.shipper_a)
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 200)

        orders = list(response.context["orders"])
        self.assertIn(self.order_a, orders)
        self.assertNotIn(self.order_b, orders)

    def test_shipper_list_excludes_soft_deleted(self):
        """Soft-deleted assigned orders are hidden from the shipper list."""
        self.order_a.is_deleted = True
        self.order_a.save(update_fields=["is_deleted"])

        self.login(self.shipper_a)
        response = self.client.get(reverse("orders:order_list"))
        self.assertNotIn(self.order_a, list(response.context["orders"]))

    # ---------- Detail isolation ----------
    def test_shipper_can_view_own_order_detail(self):
        """Shipper A can open their own assigned order (200)."""
        self.login(self.shipper_a)
        url = reverse("orders:order_detail", kwargs={"pk": self.order_a.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_shipper_detail_returns_404_for_other_shippers_order(self):
        """Shipper A opening Shipper B's order gets 404."""
        self.login(self.shipper_a)
        url = reverse("orders:order_detail", kwargs={"pk": self.order_b.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # ---------- Available orders ----------
    def test_available_orders_only_shows_unassigned_preparing(self):
        """AvailableOrdersListView returns only PREPARING + shipper=None."""
        self.login(self.shipper_a)
        response = self.client.get(reverse("orders:available_orders"))
        self.assertEqual(response.status_code, 200)

        orders = list(response.context["orders"])
        self.assertIn(self.order_c, orders)
        self.assertNotIn(self.order_a, orders)
        self.assertNotIn(self.order_b, orders)

    # ---------- Take order ----------
    def test_take_order_assigns_shipper_and_updates_status(self):
        """POST to TakeOrderView assigns shipper and advances status to SHIPPED."""
        self.login(self.shipper_a)
        url = reverse("orders:take_order", kwargs={"pk": self.order_c.pk})
        response = self.client.post(url)
        self.assertIn(response.status_code, (200, 302))

        self.order_c.refresh_from_db()
        self.assertEqual(self.order_c.shipper, self.shipper_a)
        self.assertEqual(self.order_c.status, Order.Status.SHIPPED)

    def test_cannot_take_already_assigned_order(self):
        """Shipper cannot take an order already assigned to someone else."""
        self.login(self.shipper_a)
        url = reverse("orders:take_order", kwargs={"pk": self.order_b.pk})
        response = self.client.post(url)
        self.assertIn(response.status_code, (403, 404))

        self.order_b.refresh_from_db()
        self.assertEqual(self.order_b.shipper, self.shipper_b)

    # ---------- Shipper status update ----------
    def test_shipper_can_update_own_order_to_delivered(self):
        """Shipper A can flip their own SHIPPED order to DELIVERED."""
        self.login(self.shipper_a)
        url = reverse("orders:shipper_order_update", kwargs={"pk": self.order_a.pk})
        response = self.client.post(
            url,
            {"status": Order.Status.DELIVERED, "notes": "Handed to customer."},
        )
        self.assertRedirects(response, reverse("orders:order_list"))

        self.order_a.refresh_from_db()
        self.assertEqual(self.order_a.status, Order.Status.DELIVERED)
        self.assertEqual(self.order_a.notes, "Handed to customer.")

    def test_shipper_cannot_update_another_shippers_order(self):
        """Shipper A attempting to update Shipper B's order → 404, no changes."""
        self.login(self.shipper_a)
        url = reverse("orders:shipper_order_update", kwargs={"pk": self.order_b.pk})
        response = self.client.post(
            url, {"status": Order.Status.DELIVERED, "notes": ""}
        )
        self.assertEqual(response.status_code, 404)

        self.order_b.refresh_from_db()
        self.assertEqual(self.order_b.status, Order.Status.SHIPPED)

    def test_shipper_cannot_inject_disallowed_status(self):
        """A tampered POST with CANCELLED must be rejected by the form."""
        self.login(self.shipper_a)
        url = reverse("orders:shipper_order_update", kwargs={"pk": self.order_a.pk})
        response = self.client.post(
            url, {"status": Order.Status.CANCELLED, "notes": ""}
        )
        self.assertEqual(response.status_code, 200)

        self.order_a.refresh_from_db()
        self.assertEqual(self.order_a.status, Order.Status.SHIPPED)

    def test_manager_cannot_access_shipper_only_views(self):
        """Manager must be blocked by ShipperRequiredMixin (403) when accessing shipper specific views."""
        self.login(self.manager)

        response = self.client.get(reverse("orders:available_orders"))
        self.assertEqual(response.status_code, 403)

    def test_manager_can_access_shared_order_list(self):
        """Manager should get 200 OK for the shared order list view."""
        self.login(self.manager)
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 200)
