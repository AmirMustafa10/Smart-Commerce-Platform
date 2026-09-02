import uuid
from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import Store


class StoreModelTests(TestCase):
    """Tests for the Store model."""

    def setUp(self):
        self.valid_data = {
            "name": "Test Store",
            "whatsapp_number": "+1234567890",
            "meta_api_token": "token123",
        }

    def test_create_store_success(self):
        """A Store can be created with valid data."""
        store = Store.objects.create(**self.valid_data)
        self.assertIsInstance(store.id, uuid.UUID)
        self.assertEqual(store.name, "Test Store")
        self.assertEqual(store.whatsapp_number, "+1234567890")

    def test_str_method_returns_name(self):
        """The string representation is the store's name."""
        store = Store.objects.create(**self.valid_data)
        self.assertEqual(str(store), "Test Store")

    def test_whatsapp_number_regex_validation(self):
        """Store.whatsapp_number must match E.164 format."""
        invalid_numbers = ["1234567890", "+123", "++123456", "12345678901234567"]
        for number in invalid_numbers:
            store = Store(name="Invalid Store", whatsapp_number=number)
            with self.assertRaises(ValidationError):
                store.full_clean()

    def test_whatsapp_number_unique_constraint(self):
        """Store.whatsapp_number must be unique."""
        Store.objects.create(name="First Store", whatsapp_number="+1234567890")
        duplicate = Store(name="Second Store", whatsapp_number="+1234567890")
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_name_unique_constraint(self):
        """Store.name must be unique."""
        Store.objects.create(name="Unique Store", whatsapp_number="+1234567890")
        duplicate = Store(name="Unique Store", whatsapp_number="+9999999999")
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
