import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from stores.models import Store

CustomUser = get_user_model()


class CustomUserModelTests(TestCase):
    """Tests for the CustomUser model and its manager."""

    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            whatsapp_number="+1234567890",
        )

    def test_create_user_normalizes_email_and_hashes_password(self):
        """create_user normalizes email and sets an unusable password hash."""
        user = CustomUser.objects.create_user(
            email="  TeSt@ExAmPle.com  ",
            password="strongpassword123",
            full_name="Test User",
            store=self.store,
            role=CustomUser.Role.OWNER,
        ) # pyright: ignore[reportCallIssue]
        self.assertEqual(user.email, "test@example.com")  # normalized
        self.assertTrue(user.check_password("strongpassword123"))
        self.assertNotEqual(user.password, "strongpassword123")
        self.assertTrue(user.is_active)  # default True
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.store, self.store)
        self.assertEqual(user.role, CustomUser.Role.OWNER)

    def test_create_superuser_has_correct_flags_and_store_none(self):
        """create_superuser sets is_staff, is_superuser, and store=None."""
        superuser = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            full_name="Admin User",
        ) # pyright: ignore[reportCallIssue]
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertIsNone(superuser.store)
        self.assertTrue(superuser.is_active)
        # role defaults to OWNER as per manager
        self.assertEqual(superuser.role, CustomUser.Role.OWNER)

    def test_str_method_returns_email(self):
        """The string representation is the user's email."""
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="pass12345",
            full_name="User",
            store=self.store,
            role=CustomUser.Role.SHIPPER,
        ) # pyright: ignore[reportCallIssue]
        self.assertEqual(str(user), "user@example.com")

    def test_user_id_is_uuid(self):
        """CustomUser.id is a UUID."""
        user = CustomUser.objects.create_user(
            email="uuid@example.com",
            password="pass12345",
            full_name="UUID User",
            store=self.store,
            role=CustomUser.Role.OWNER,
        ) # pyright: ignore[reportCallIssue]
        self.assertIsInstance(user.id, uuid.UUID)
