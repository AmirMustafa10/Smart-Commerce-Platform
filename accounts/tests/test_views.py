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
        self.dashboard_url = reverse("core:dashboard")
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


class AccountsViewsTest(TestCase):
    """Comprehensive tests for account-related views."""

    @classmethod
    def setUpTestData(cls):
        # Create stores
        cls.store_a = Store.objects.create(
            name="Store A",
            whatsapp_number="+1111111111",
        )
        cls.store_b = Store.objects.create(
            name="Store B",
            whatsapp_number="+2222222222",
        )

        # Create users for Store A
        cls.owner_a = CustomUser.objects.create_user(
            email="owner_a@example.com",
            password="password123",
            full_name="Owner A",
            store=cls.store_a,
            role=CustomUser.Role.OWNER,
        )  # pyright: ignore[reportCallIssue]
        cls.shipper_a = CustomUser.objects.create_user(
            email="shipper_a@example.com",
            password="password123",
            full_name="Shipper A",
            store=cls.store_a,
            role=CustomUser.Role.SHIPPER,
        )  # pyright: ignore[reportCallIssue]

        # Create users for Store B
        cls.owner_b = CustomUser.objects.create_user(
            email="owner_b@example.com",
            password="password123",
            full_name="Owner B",
            store=cls.store_b,
            role=CustomUser.Role.OWNER,
        )  # pyright: ignore[reportCallIssue]
        cls.shipper_b = CustomUser.objects.create_user(
            email="shipper_b@example.com",
            password="password123",
            full_name="Shipper B",
            store=cls.store_b,
            role=CustomUser.Role.SHIPPER,
        )  # pyright: ignore[reportCallIssue]

        # URL names (adjust if different in your project)
        cls.team_list_url = reverse("accounts:team_list")
        cls.shipper_create_url = reverse("accounts:shipper_create")
        # For toggle: assume URL pattern includes pk
        cls.toggle_url = lambda pk: reverse(
            "accounts:shipper_toggle", kwargs={"pk": pk}
        )
        # SmartProfile URLs: one without pk, one with pk
        cls.my_profile_url = reverse("accounts:my_profile")
        cls.member_profile_url = lambda pk: reverse(
            "accounts:member_profile", kwargs={"pk": pk}
        )
        cls.profile_update_url = reverse("accounts:profile_edit")
        cls.password_change_url = reverse("accounts:password_change")

    def login(self, user):
        """Helper to login as a given user."""
        self.client.login(email=user.email, password="password123")

    # ------------------------------------------------------------------
    # TeamListView Tests
    # ------------------------------------------------------------------
    def test_team_list_unauthenticated_redirect(self):
        response = self.client.get(self.team_list_url)
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.team_list_url}",
            status_code=302,
        )

    def test_team_list_owner_a_sees_only_own_shippers(self):
        self.login(self.owner_a)
        response = self.client.get(self.team_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shipper A")
        self.assertNotContains(response, "Shipper B")

    def test_team_list_context_contains_owner(self):
        self.login(self.owner_a)
        response = self.client.get(self.team_list_url)
        self.assertEqual(response.context["owner"], self.owner_a)

    def test_team_list_shipper_can_access(self):
        self.login(self.shipper_a)
        response = self.client.get(self.team_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shipper A")
        self.assertNotContains(response, "Shipper B")

    # ------------------------------------------------------------------
    # ShipperCreateView Tests
    # ------------------------------------------------------------------
    def test_shipper_create_shipper_forbidden(self):
        self.login(self.shipper_a)
        response = self.client.get(self.shipper_create_url)
        self.assertEqual(response.status_code, 403)

    def test_shipper_create_owner_post_creates_user(self):
        self.login(self.owner_a)
        data = {
            "full_name": "New Shipper",
            "email": "new_shipper@example.com",
            "password": "newpassword123",
        }
        response = self.client.post(self.shipper_create_url, data)
        self.assertRedirects(response, self.team_list_url, status_code=302)

        # Verify user was created
        new_user = CustomUser.objects.get(email="new_shipper@example.com")
        self.assertEqual(new_user.full_name, "New Shipper")
        self.assertEqual(new_user.store, self.store_a)
        self.assertEqual(new_user.role, CustomUser.Role.SHIPPER)
        self.assertTrue(new_user.check_password("newpassword123"))

    # ------------------------------------------------------------------
    # ShipperToggleStatusView Tests
    # ------------------------------------------------------------------
    def test_toggle_get_not_allowed(self):
        self.login(self.owner_a)
        response = self.client.get(self.toggle_url(self.shipper_a.pk))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_toggle_shipper_forbidden(self):
        self.login(self.shipper_a)
        response = self.client.post(self.toggle_url(self.shipper_a.pk))
        self.assertEqual(response.status_code, 403)

    def test_toggle_owner_toggles_own_shipper(self):
        self.login(self.owner_a)
        # Initial state
        self.assertTrue(self.shipper_a.is_active)
        response = self.client.post(self.toggle_url(self.shipper_a.pk))
        self.assertEqual(response.status_code, 302)  # redirect after toggle
        self.shipper_a.refresh_from_db()
        self.assertFalse(self.shipper_a.is_active)

        # Toggle again
        response = self.client.post(self.toggle_url(self.shipper_a.pk))
        self.shipper_a.refresh_from_db()
        self.assertTrue(self.shipper_a.is_active)

    def test_toggle_isolation_owner_a_cannot_toggle_other_store_shipper(self):
        self.login(self.owner_a)
        response = self.client.post(self.toggle_url(self.shipper_b.pk))
        self.assertEqual(
            response.status_code, 404
        )  # Not Found due to filtered queryset

    # ------------------------------------------------------------------
    # SmartProfileView Tests
    # ------------------------------------------------------------------
    def test_profile_without_pk_returns_current_user(self):
        self.login(self.shipper_a)
        response = self.client.get(self.my_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.shipper_a)

    def test_profile_with_pk_owner_views_shipper(self):
        self.login(self.owner_a)
        response = self.client.get(self.member_profile_url(self.shipper_a.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.shipper_a)

    def test_profile_isolation_owner_a_cannot_view_other_store_shipper(self):
        self.login(self.owner_a)
        response = self.client.get(self.member_profile_url(self.shipper_b.pk))
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # UserProfileUpdateView Tests
    # ------------------------------------------------------------------
    def test_profile_update_updates_current_user(self):
        self.login(self.owner_a)
        data = {
            "full_name": "Updated Owner A",
            "email": "updated_owner_a@example.com",
        }
        response = self.client.post(self.profile_update_url, data)
        self.assertRedirects(response, self.my_profile_url, status_code=302)
        self.owner_a.refresh_from_db()
        self.assertEqual(self.owner_a.full_name, "Updated Owner A")
        self.assertEqual(self.owner_a.email, "updated_owner_a@example.com")

    # ------------------------------------------------------------------
    # CustomPasswordChangeView Tests
    # ------------------------------------------------------------------
    def test_password_change_success(self):
        self.login(self.owner_a)
        data = {
            "old_password": "password123",
            "new_password1": "newSecurePass456",
            "new_password2": "newSecurePass456",
        }
        response = self.client.post(self.password_change_url, data)
        self.assertEqual(response.status_code, 302)  # redirect after success

        # Verify new password works
        self.owner_a.refresh_from_db()
        self.assertTrue(self.owner_a.check_password("newSecurePass456"))
        # Also verify old password fails
        self.assertFalse(self.owner_a.check_password("password123"))
