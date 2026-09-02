from django.test import TestCase
from django.contrib.auth import get_user_model
from stores.models import Store
from ..forms import MerchantSignUpForm, UserProfileUpdateForm, ShipperCreationForm

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


class ShipperCreationFormTest(TestCase):
    """Tests for ShipperCreationForm."""

    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store", whatsapp_number="+1234567890"
        )

        self.valid_data = {
            "full_name": "John Doe",
            "email": "shipper@example.com",
            "password": "strongpassword123",
        }

    def get_dummy_instance(self):
        return CustomUser(store=self.store, role=CustomUser.Role.SHIPPER)

    def test_valid_data_saves_user_with_hashed_password(self):
        """Form is valid, saves user, and hashes password correctly."""
        form = ShipperCreationForm(
            data=self.valid_data, instance=self.get_dummy_instance()
        )

        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertIsNotNone(user.pk)
        self.assertEqual(user.full_name, "John Doe")
        self.assertEqual(user.email, "shipper@example.com")
        self.assertEqual(user.store, self.store)
        self.assertTrue(user.check_password("strongpassword123"))
        self.assertNotEqual(user.password, "strongpassword123")  # ensure hashed

    def test_email_normalization(self):
        """Email is stripped and lowercased during cleaning."""
        data = self.valid_data.copy()
        data["email"] = "  Test@EXAMPLE.com "

        form = ShipperCreationForm(data=data, instance=self.get_dummy_instance())
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "test@example.com")

    def test_duplicate_email_rejected(self):
        """Form is invalid if email already exists in database."""
        CustomUser.objects.create_user(
            email="shipper@example.com",
            password="password123",
            full_name="Existing User",
            store=self.store,
            role=CustomUser.Role.SHIPPER,
        ) # pyright: ignore[reportCallIssue]

        form = ShipperCreationForm(
            data=self.valid_data, instance=self.get_dummy_instance()
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_fields(self):
        """Form is invalid if any required field is missing."""
        # Missing password
        data = self.valid_data.copy()
        data.pop("password")
        form = ShipperCreationForm(data=data, instance=self.get_dummy_instance())
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

        # Missing email
        data = self.valid_data.copy()
        data.pop("email")
        form = ShipperCreationForm(data=data, instance=self.get_dummy_instance())
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

        # Missing full_name
        data = self.valid_data.copy()
        data.pop("full_name")
        form = ShipperCreationForm(data=data, instance=self.get_dummy_instance())
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)


class UserProfileUpdateFormTest(TestCase):
    """Tests for UserProfileUpdateForm."""

    def setUp(self):
        from stores.models import Store

        self.store = Store.objects.create(
            name="Test Store", whatsapp_number="+1234567890"
        )
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password="password123",
            full_name="Original Name",
            store=self.store,
            role=CustomUser.Role.OWNER,
        ) # pyright: ignore[reportCallIssue]

    def test_valid_update(self):
        """Form is valid and updates full_name and email."""
        data = {
            "full_name": "Updated Name",
            "email": "updated@example.com",
        }
        form = UserProfileUpdateForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.full_name, "Updated Name")
        self.assertEqual(updated_user.email, "updated@example.com")

    def test_same_email_update_valid(self):
        """Form is valid when submitting the same email as the instance."""
        data = {
            "full_name": "Still Original",
            "email": self.user.email,  # unchanged
        }
        form = UserProfileUpdateForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_email_taken_by_other_user_rejected(self):
        """Form is invalid if email belongs to a different user."""
        other_user = CustomUser.objects.create_user(
            email="other@example.com",
            password="password123",
            full_name="Other User",
            store=self.store,
            role=CustomUser.Role.SHIPPER,
        ) # pyright: ignore[reportCallIssue]
        data = {
            "full_name": "New Name",
            "email": other_user.email,  # taken
        }
        form = UserProfileUpdateForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_normalization(self):
        """Email is stripped and lowercased during cleaning."""
        data = {
            "full_name": "Normalized",
            "email": "  UPDATED@EXAMPLE.COM ",
        }
        form = UserProfileUpdateForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "updated@example.com")
