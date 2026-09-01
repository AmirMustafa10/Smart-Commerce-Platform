from django.test import TestCase
from django.contrib.auth import get_user_model
from stores.models import Store
from ..forms import MerchantSignUpForm

CustomUser = get_user_model()


class MerchantSignUpFormTests(TestCase):
    """Tests for the MerchantSignUpForm."""

    def setUp(self):
        self.store = Store.objects.create(
            name="Existing Store",
            whatsapp_number="+1111111111",
        )
        self.user = CustomUser.objects.create_user(
            email="existing@example.com",
            password="password123",
            full_name="Existing User",
            store=self.store,
            role=CustomUser.Role.OWNER,
        ) # pyright: ignore[reportCallIssue]

    def test_form_with_valid_data_is_valid(self):
        """The form is valid when all required fields are provided correctly."""
        form_data = {
            "store_name": "New Store",
            "full_name": "New User",
            "email": "new@example.com",
            "whatsapp_number": "+201012345678",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        }
        form = MerchantSignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_duplicate_store_name(self):
        """The form rejects a store name that already exists (case‑insensitive)."""
        form_data = {
            "store_name": "existing store",  # same as existing, different case
            "full_name": "Another User",
            "email": "another@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        form = MerchantSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("store_name", form.errors)

    def test_form_rejects_duplicate_email(self):
        """The form rejects an email that already exists (case‑insensitive)."""
        form_data = {
            "store_name": "Another Store",
            "full_name": "Another User",
            "email": "EXISTING@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        form = MerchantSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_rejects_password_mismatch(self):
        """The form rejects when password and confirm_password do not match."""
        form_data = {
            "store_name": "Another Store",
            "full_name": "Another User",
            "email": "another@example.com",
            "password": "password123",
            "confirm_password": "different123",
        }
        form = MerchantSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)
