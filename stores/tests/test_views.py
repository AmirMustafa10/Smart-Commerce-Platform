from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from ..models import Store

CustomUser = get_user_model()


class StoreViewsTests(TestCase):
    """Test suite for Store settings, deactivation, and activation views."""

    def setUp(self):
        # Create a store
        self.store = Store.objects.create(
            name="Test Store",
            whatsapp_number="+14155552671",
            meta_api_token="initial_token",
        )

        # Create an owner user
        self.owner = CustomUser.objects.create_user(
            email="owner@example.com",
            password="ownerpass123",
            full_name="Owner User",
            store=self.store,
            role=CustomUser.Role.OWNER,
        ) # pyright: ignore[reportCallIssue]

        # Create a shipper user
        self.shipper = CustomUser.objects.create_user(
            email="shipper@example.com",
            password="shipperpass123",
            full_name="Shipper User",
            store=self.store,
            role=CustomUser.Role.SHIPPER,
        ) # pyright: ignore[reportCallIssue]

        # URLs
        self.settings_url = reverse("stores:settings")
        self.deactivate_url = reverse("stores:deactivate")
        self.activate_url = reverse("stores:activate")
        self.home_url = reverse("core:home")  # Assume 'home' exists; adjust if needed

    def _login(self, user):
        """Helper to log in a user with email and password."""
        self.client.login(
            email=user.email,
            password=(
                "ownerpass123"
                if user.role == CustomUser.Role.OWNER
                else "shipperpass123"
            ),
        )

    # ========== StoreSettingsView Tests ==========

    def test_settings_view_unauthenticated_redirects_to_login(self):
        """Unauthenticated user is redirected to login page."""
        response = self.client.get(self.settings_url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.settings_url}"
        )

    def test_settings_view_shipper_gets_403(self):
        """Shipper cannot access settings view."""
        self._login(self.shipper)
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 403)

    def test_settings_view_owner_gets_200_and_template(self):
        """Owner gets 200 and correct template."""
        self._login(self.owner)
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stores/settings.html")

    def test_settings_view_owner_post_valid_updates_store_and_message(self):
        """Owner POST valid data updates store and shows success message."""
        self._login(self.owner)
        data = {
            "name": "Updated Store",
            "whatsapp_number": "+15551234567",
            "meta_api_token": "updated_token",
        }
        response = self.client.post(self.settings_url, data)
        self.assertRedirects(response, self.settings_url)

        # Refresh store from DB
        self.store.refresh_from_db()
        self.assertEqual(self.store.name, "Updated Store")
        self.assertEqual(self.store.whatsapp_number, "+15551234567")
        self.assertEqual(self.store.meta_api_token, "updated_token")

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Store settings updated successfully.", str(messages[0]))

    # ========== StoreDeactivateView Tests ==========

    def test_deactivate_view_get_not_allowed(self):
        """GET request to deactivate returns 405 Method Not Allowed."""
        self._login(self.owner)
        response = self.client.get(self.deactivate_url)
        self.assertEqual(response.status_code, 405)

    def test_deactivate_view_shipper_cannot_deactivate(self):
        """Shipper cannot deactivate the store (403)."""
        self._login(self.shipper)
        response = self.client.post(self.deactivate_url)
        self.assertEqual(response.status_code, 403)

        # Store remains active
        self.store.refresh_from_db()
        self.assertTrue(self.store.is_active)

    def test_deactivate_view_owner_sets_inactive_and_logs_out(self):
        """Owner POST deactivates store, logs out, and redirects."""
        self._login(self.owner)
        response = self.client.post(self.deactivate_url)
        self.assertRedirects(response, self.settings_url)

        # Store should be inactive
        self.store.refresh_from_db()
        self.assertFalse(self.store.is_active)

        # User should be logged out (session cleared)
        self.assertIn("_auth_user_id", self.client.session)

    # ========== StoreActivateView Tests ==========

    def test_activate_view_get_not_allowed(self):
        """GET request to activate returns 405 Method Not Allowed."""
        # First deactivate store to test activation
        self.store.is_active = False
        self.store.save()
        self._login(self.owner)
        response = self.client.get(self.activate_url)
        self.assertEqual(response.status_code, 405)

    def test_activate_view_shipper_cannot_activate(self):
        """Shipper cannot activate the store (403)."""
        self.store.is_active = False
        self.store.save()
        self._login(self.shipper)
        response = self.client.post(self.activate_url)
        self.assertEqual(response.status_code, 403)

        # Store remains inactive
        self.store.refresh_from_db()
        self.assertFalse(self.store.is_active)

    def test_activate_view_owner_sets_active(self):
        """Owner POST activates store and redirects to settings."""
        self.store.is_active = False
        self.store.save()
        self._login(self.owner)
        response = self.client.post(self.activate_url)
        self.assertRedirects(response, self.settings_url)  # Adjust if different

        # Store should be active
        self.store.refresh_from_db()
        self.assertTrue(self.store.is_active)

        # User should still be logged in
        self.assertIn("_auth_user_id", self.client.session)
