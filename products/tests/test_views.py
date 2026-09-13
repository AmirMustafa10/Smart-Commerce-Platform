from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from stores.models import Store
from products.models import Category, Product

User = get_user_model()


class CategoryViewRBACAndTenantIsolationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Stores
        cls.store_a = Store.objects.create(
            name="Store A", whatsapp_number="+1111111111"
        )
        cls.store_b = Store.objects.create(
            name="Store B", whatsapp_number="+2222222222"
        )

        # Users for Store A
        cls.owner_a = User.objects.create_user(
            email="owner_a@example.com",
            password="pass123",
            full_name="Owner A",
            store=cls.store_a,
            role=User.Role.OWNER,
        )
        cls.manager_a = User.objects.create_user(
            email="manager_a@example.com",
            password="pass123",
            full_name="Manager A",
            store=cls.store_a,
            role=User.Role.MANAGER,
        )
        cls.shipper_a = User.objects.create_user(
            email="shipper_a@example.com",
            password="pass123",
            full_name="Shipper A",
            store=cls.store_a,
            role=User.Role.SHIPPER,
        )

        # User for Store B (owner)
        cls.owner_b = User.objects.create_user(
            email="owner_b@example.com",
            password="pass123",
            full_name="Owner B",
            store=cls.store_b,
            role=User.Role.OWNER,
        )

        # Categories
        cls.cat_a = Category.objects.create(store=cls.store_a, name="Cat A")
        cls.cat_b = Category.objects.create(store=cls.store_b, name="Cat B")

        # URLs
        cls.list_url = reverse("products:category_list")
        cls.create_url = reverse("products:category_create")
        cls.update_url_a = reverse(
            "products:category_update", kwargs={"pk": cls.cat_a.pk}
        )
        cls.delete_url_a = reverse(
            "products:category_delete", kwargs={"pk": cls.cat_a.pk}
        )

    def login(self, user):
        self.client.login(email=user.email, password="pass123")

    # --- RBAC Tests ---
    def test_owner_can_access_list(self):
        self.login(self.owner_a)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_manager_can_access_list(self):
        self.login(self.manager_a)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_shipper_forbidden_from_list(self):
        self.login(self.shipper_a)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)

    # --- Tenant Isolation Tests ---
    def test_list_shows_only_own_categories(self):
        self.login(self.owner_a)
        response = self.client.get(self.list_url)
        self.assertContains(response, "Cat A")
        self.assertNotContains(response, "Cat B")

    def test_update_other_store_returns_404(self):
        self.login(self.owner_a)
        update_url_b = reverse("products:category_update", kwargs={"pk": self.cat_b.pk})
        response = self.client.get(update_url_b)
        self.assertEqual(response.status_code, 404)

    def test_delete_other_store_returns_404(self):
        self.login(self.owner_a)
        delete_url_b = reverse("products:category_delete", kwargs={"pk": self.cat_b.pk})
        response = self.client.post(delete_url_b)
        self.assertEqual(response.status_code, 404)


class CategoryDeleteSoftDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(name="Store", whatsapp_number="+4444444444")
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass123",
            full_name="Owner",
            store=cls.store,
            role=User.Role.OWNER,
        )  # pyright: ignore[reportCallIssue]
        cls.category = Category.objects.create(store=cls.store, name="To Delete")
        cls.delete_url = reverse(
            "products:category_delete", kwargs={"pk": cls.category.pk}
        )

    def test_delete_view_performs_soft_delete(self):
        self.client.login(email="owner@example.com", password="pass123")
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse("products:category_list"))

        self.category.refresh_from_db()
        self.assertTrue(self.category.is_deleted)
        self.assertTrue(Category.all_objects.filter(pk=self.category.pk).exists())


class ProductViewStoreInjectionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(name="Store", whatsapp_number="+5555555555")
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass123",
            full_name="Owner",
            store=cls.store,
            role=User.Role.OWNER,
        )  # pyright: ignore[reportCallIssue]
        cls.category = Category.objects.create(store=cls.store, name="Cat")
        cls.create_url = reverse("products:product_create")

    def test_product_create_assigns_store_automatically(self):
        self.client.login(email="owner@example.com", password="pass123")
        data = {
            "name": "New Product",
            "category": self.category.pk,
            "price": "10.00",
            "stock_quantity": 5,
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)  # redirect to list
        product = Product.objects.get(name="New Product")
        self.assertEqual(product.store, self.store)
        self.assertEqual(product.category.store, self.store)
