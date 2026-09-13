from django.test import TestCase
from django.contrib.auth import get_user_model
from stores.models import Store
from products.models import Category, Product
from products.forms import CategoryForm, ProductForm

User = get_user_model()


class ProductFormTenantFilteringTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.store_a = Store.objects.create(
            name="Store A", whatsapp_number="+1111111111"
        )
        cls.store_b = Store.objects.create(
            name="Store B", whatsapp_number="+2222222222"
        )
        cls.cat_a_active = Category.objects.create(
            store=cls.store_a, name="A Active", is_active=True
        )
        cls.cat_a_inactive = Category.objects.create(
            store=cls.store_a, name="A Inactive", is_active=False
        )
        cls.cat_b_active = Category.objects.create(
            store=cls.store_b, name="B Active", is_active=True
        )

    def test_product_form_filters_categories_by_store_and_active(self):
        form = ProductForm(store=self.store_a)
        queryset = form.fields["category"].queryset
        self.assertIn(self.cat_a_active, queryset)
        self.assertNotIn(self.cat_a_inactive, queryset)  # inactive excluded
        self.assertNotIn(self.cat_b_active, queryset)  # other store excluded

    def test_product_form_with_no_store_has_empty_category_queryset(self):
        form = ProductForm()
        self.assertEqual(form.fields["category"].queryset.count(), 0)


class CategoryFormUniqueWithSoftDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(name="Store", whatsapp_number="+3333333333")
        cls.active_category = Category.objects.create(
            store=cls.store, name="Duplicate Name"
        )

    def test_duplicate_active_category_name_is_invalid(self):
        form = CategoryForm(data={"name": "Duplicate Name", "is_active": True})
        # Need to inject store? The form does not have store field; unique check is at model level,
        # and ModelForm validation uses the instance's store. For create, we may need to assign store in get_form_kwargs.
        # In views, store is assigned before validation; but here we simulate by setting instance.store.
        form.instance.store = self.store
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_duplicate_soft_deleted_category_name_is_valid(self):
        # Soft delete the active category
        self.active_category.is_deleted = True
        self.active_category.save()

        form = CategoryForm(data={"name": "Duplicate Name", "is_active": True})
        form.instance.store = self.store
        self.assertTrue(form.is_valid())
