from django.test import TestCase
from django.urls import reverse
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
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_post_valid_data_creates_store_and_user_and_redirects(self):
        data = {
            "store_name": "New Store",
            "full_name": "New User",
            "email": "new@example.com",
            "whatsapp_number": "+201012345678",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        }
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(
            response, self.dashboard_url, status_code=302, target_status_code=200
        )
        store = Store.objects.filter(name="New Store").first()
        self.assertIsNotNone(store)
        user = CustomUser.objects.filter(email="new@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.store, store)
        self.assertEqual(user.role, CustomUser.Role.OWNER)

    def test_post_invalid_data_does_not_create_any_objects(self):
        data = {
            "store_name": "Another Store",
            "full_name": "Another User",
            "email": "another@example.com",
            "password": "password123",
            "confirm_password": "mismatch123",  # invalid
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")
        self.assertFalse(Store.objects.filter(name="Another Store").exists())
        self.assertFalse(
            CustomUser.objects.filter(email="another@example.com").exists()
        )


class AccountsViewsTest(TestCase):
    """Comprehensive tests for account-related views (Team Management)."""

    @classmethod
    def setUpTestData(cls):
        # Create stores
        cls.store_a = Store.objects.create(
            name="Store A", whatsapp_number="+1111111111"
        )
        cls.store_b = Store.objects.create(
            name="Store B", whatsapp_number="+2222222222"
        )

        # Create users for Store A
        cls.owner_a = CustomUser.objects.create_user(
            email="owner_a@example.com",
            password="password123",
            full_name="Owner A",
            store=cls.store_a,
            role=CustomUser.Role.OWNER,
        )  # pyright: ignore[reportCallIssue]

        # ضفنا Manager للتيست
        cls.manager_a = CustomUser.objects.create_user(
            email="manager_a@example.com",
            password="password123",
            full_name="Manager A",
            store=cls.store_a,
            role=CustomUser.Role.MANAGER,
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

        cls.team_list_url = reverse("accounts:team_list")
        cls.member_create_url = reverse("accounts:team_member_create")
        cls.toggle_url = lambda pk: reverse(
            "accounts:team_member_toggle", kwargs={"pk": pk}
        )

        cls.my_profile_url = reverse("accounts:my_profile")
        cls.member_profile_url = lambda pk: reverse(
            "accounts:member_profile", kwargs={"pk": pk}
        )
        cls.profile_update_url = reverse("accounts:profile_edit")
        cls.password_change_url = reverse("accounts:password_change")

    def login(self, user):
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

    def test_team_list_owner_a_sees_only_own_team(self):
        self.login(self.owner_a)
        response = self.client.get(self.team_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shipper A")
        self.assertContains(response, "Manager A")
        self.assertNotContains(response, "Shipper B")

    # ------------------------------------------------------------------
    # TeamMemberCreateView Tests
    # ------------------------------------------------------------------
    def test_member_create_shipper_forbidden(self):
        self.login(self.shipper_a)
        response = self.client.get(self.member_create_url)
        self.assertEqual(response.status_code, 403)

    def test_member_create_manager_forbidden(self):
        """Manager should not be able to create new team members."""
        self.login(self.manager_a)
        response = self.client.get(self.member_create_url)
        self.assertEqual(response.status_code, 403)

    def test_member_create_owner_post_creates_manager(self):
        self.login(self.owner_a)
        data = {
            "full_name": "New Manager",
            "email": "new_manager@example.com",
            "password": "newpassword123",
            "role": CustomUser.Role.MANAGER,
        }
        response = self.client.post(self.member_create_url, data)
        self.assertRedirects(response, self.team_list_url, status_code=302)

        new_user = CustomUser.objects.get(email="new_manager@example.com")
        self.assertEqual(new_user.role, CustomUser.Role.MANAGER)
        self.assertEqual(new_user.store, self.store_a)

    # ------------------------------------------------------------------
    # TeamMemberToggleStatusView Tests
    # ------------------------------------------------------------------
    def test_toggle_get_not_allowed(self):
        self.login(self.owner_a)
        response = self.client.get(self.toggle_url(self.shipper_a.pk))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_toggle_owner_toggles_manager(self):
        """Owner can successfully toggle a Manager."""
        self.login(self.owner_a)
        self.assertTrue(self.manager_a.is_active)
        response = self.client.post(self.toggle_url(self.manager_a.pk))
        self.assertEqual(response.status_code, 302)
        self.manager_a.refresh_from_db()
        self.assertFalse(self.manager_a.is_active)

    def test_toggle_isolation_owner_a_cannot_toggle_other_store_shipper(self):
        self.login(self.owner_a)
        response = self.client.post(self.toggle_url(self.shipper_b.pk))
        self.assertEqual(response.status_code, 404)

    def test_toggle_security_owner_cannot_toggle_self(self):
        """Critical Security: Owner cannot toggle themselves because the queryset restricts to MANAGER/SHIPPER."""
        self.login(self.owner_a)
        response = self.client.post(self.toggle_url(self.owner_a.pk))
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # SmartProfileView Tests & UserProfileUpdateView Tests
    # ------------------------------------------------------------------
    def test_profile_without_pk_returns_current_user(self):
        self.login(self.shipper_a)
        response = self.client.get(self.my_profile_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update_updates_current_user(self):
        self.login(self.owner_a)
        data = {
            "full_name": "Updated Owner A",
            "email": "updated_owner_a@example.com",
        }
        response = self.client.post(self.profile_update_url, data)
        self.assertRedirects(response, self.my_profile_url, status_code=302)
