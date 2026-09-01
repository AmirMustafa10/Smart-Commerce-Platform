from django.test import TestCase
from django.urls import reverse
from uuid import UUID
from django.contrib.auth import get_user_model
from stores.models import Store

CustomUser = get_user_model()


class MerchantSignUpViewTests(TestCase):
    """Tests for the merchant sign‑up view."""

    def setUp(self):
        self.signup_url = reverse("accounts:signup")
        self.dashboard_url = reverse("core:home")
        self.login_url = reverse("accounts:login")

    def test_get_signup_page_returns_200_and_uses_correct_template(self):
        """GET /signup/ returns 200 and uses the signup template."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_post_valid_data_creates_store_and_user_and_redirects(self):
        """Submitting valid signup data creates Store + User, logs in, and redirects to dashboard."""
        data = {
            "store_name": "New Store",
            "full_name": "New User",
            "email": "new@example.com",
            "whatsapp_number": "+201012345678",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        }
        response = self.client.post(self.signup_url, data)

        # Check redirect to dashboard
        self.assertRedirects(
            response, self.dashboard_url, status_code=302, target_status_code=200
        )

        # Check Store created
        store = Store.objects.filter(name="New Store").first()
        self.assertIsNotNone(store)

        # Check user created and linked to store
        user = CustomUser.objects.filter(email="new@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.store, store)
        self.assertEqual(user.role, CustomUser.Role.OWNER)

        # Check user is logged in (session contains user id)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(UUID(self.client.session["_auth_user_id"]), user.id)

    def test_post_invalid_data_does_not_create_any_objects(self):
        """If form is invalid, neither Store nor User are created (atomic transaction)."""
        data = {
            "store_name": "Another Store",
            "full_name": "Another User",
            "email": "another@example.com",
            "password": "password123",
            "confirm_password": "mismatch123",  # invalid
        }
        response = self.client.post(self.signup_url, data)

        # Response should be 200 (re-render form)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

        # No Store or User should exist
        self.assertFalse(Store.objects.filter(name="Another Store").exists())
        self.assertFalse(
            CustomUser.objects.filter(email="another@example.com").exists()
        )


class DashboardViewTests(TestCase):
    """Tests for the dashboard view."""

    def setUp(self):
        self.dashboard_url = reverse("core:home")
        self.login_url = reverse("accounts:login")
        # Create a store and user for authenticated test
        self.store = Store.objects.create(
            name="Test Store", whatsapp_number="+1234567890"
        )
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password="password123",
            full_name="Test User",
            store=self.store,
            role=CustomUser.Role.OWNER,
        ) # pyright: ignore[reportCallIssue]

    def test_unauthenticated_user_redirected_to_login(self):
        """An unauthenticated request to dashboard redirects to login."""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.dashboard_url}")

    def test_authenticated_user_gets_200(self):
        """An authenticated user receives a 200 status on dashboard."""
        self.client.login(email="user@example.com", password="password123")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/dashboard.html")
