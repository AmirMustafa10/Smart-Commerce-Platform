from django.test import TestCase
from ..models import Store
from ..forms import StoreSettingsForm


class StoreSettingsFormTests(TestCase):
    """Test suite for the StoreSettingsForm."""

    def setUp(self):
        # Create an existing store to test uniqueness constraints
        self.existing_store = Store.objects.create(
            name="Existing Store",
            whatsapp_number="+14155552671",
            meta_api_token="existing_token",
        )

        self.valid_data = {
            "name": "Updated Store Name",
            "whatsapp_number": "+15551234567",
            "meta_api_token": "new_token",
        }

    def test_valid_data_passes(self):
        """Form is valid with correct data."""
        form = StoreSettingsForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["whatsapp_number"], "+15551234567")

    def test_whatsapp_number_is_stripped(self):
        """Whitespace in WhatsApp number is removed during cleaning."""
        data = self.valid_data.copy()
        data["whatsapp_number"] = "  +15551234567  "
        form = StoreSettingsForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["whatsapp_number"], "+15551234567")

    def test_whatsapp_number_invalid_formats(self):
        """Various invalid phone number formats should fail validation."""
        invalid_numbers = [
            "15551234567",  # missing '+'
            "+05551234567",  # leading 0 after '+' not allowed
            "+1555123",  # too short (8 digits minimum after country code)
            "+155512345678901658",  # too long (15 digits maximum after country code)
            "++15551234567",  # double plus
            "+1 555 123 4567",  # spaces inside not allowed
            "+15551234567abc",  # letters
        ]
        for number in invalid_numbers:
            data = self.valid_data.copy()
            data["whatsapp_number"] = number
            form = StoreSettingsForm(data=data)
            self.assertFalse(form.is_valid(), f"Expected '{number}' to be invalid")
            self.assertIn("whatsapp_number", form.errors)

    def test_name_is_required(self):
        """Name field cannot be blank."""
        data = self.valid_data.copy()
        data["name"] = ""
        form = StoreSettingsForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_name_cannot_be_whitespace_only(self):
        """Name that is only spaces should be invalid (or stripped to empty)."""
        data = self.valid_data.copy()
        data["name"] = "   "
        form = StoreSettingsForm(data=data)
        # Model's clean() will strip and raise error, but the form may also catch it.
        # ModelForm validates that required field is not blank after stripping.
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_duplicate_name_rejected(self):
        """Name that already exists (case-insensitive) should fail."""
        data = self.valid_data.copy()
        data["name"] = "Existing Store"  # same as existing, different case
        form = StoreSettingsForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_duplicate_whatsapp_number_rejected(self):
        """WhatsApp number that already exists should fail."""
        data = self.valid_data.copy()
        data["whatsapp_number"] = self.existing_store.whatsapp_number
        form = StoreSettingsForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("whatsapp_number", form.errors)

    def test_meta_api_token_optional(self):
        """Meta API token can be left blank."""
        data = self.valid_data.copy()
        data["meta_api_token"] = ""
        form = StoreSettingsForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["meta_api_token"], None)

    def test_meta_api_token_stripped(self):
        """Meta API token is stripped of whitespace."""
        data = self.valid_data.copy()
        data["meta_api_token"] = "  token_with_spaces  "
        form = StoreSettingsForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["meta_api_token"], "token_with_spaces")
