from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from stores.models import Store

CustomUser = get_user_model()


class DashboardViewTests(TestCase):
    """Tests for the dashboard view."""

    def setUp(self):
        self.dashboard_url = reverse("core:dashboard")
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
        )  # pyright: ignore[reportCallIssue]

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
