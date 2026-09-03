from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from stores.models import Store
from ..models import Category, Product, ProductImage
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image


def get_dummy_image(self, name="test.jpg"):
    img_io = BytesIO()
    image = Image.new("RGB", (1, 1), "white")
    image.save(img_io, format="JPEG")
    img_io.seek(0)
    return SimpleUploadedFile(name, img_io.read(), content_type="image/jpeg")


class ProductModelsTest(TestCase):
    """Comprehensive tests for Category, Product, and ProductImage models."""

    @classmethod
    def setUpTestData(cls):
        # Create two stores
        cls.store_a = Store.objects.create(
            name="Store A",
            whatsapp_number="+1111111111",
        )
        cls.store_b = Store.objects.create(
            name="Store B",
            whatsapp_number="+2222222222",
        )

        # Create categories for both stores
        cls.category_a1 = Category.objects.create(
            store=cls.store_a,
            name="Category A1",
        )
        cls.category_a2 = Category.objects.create(
            store=cls.store_a,
            name="Category A2",
        )
        cls.category_b1 = Category.objects.create(
            store=cls.store_b,
            name="Category B1",
        )

        # Create products for Store A
        cls.product_a1 = Product.objects.create(
            store=cls.store_a,
            category=cls.category_a1,
            name="Product A1",
            sku="SKU-A1",
            price=Decimal("100.00"),
            stock_quantity=5,
        )
        cls.product_a2 = Product.objects.create(
            store=cls.store_a,
            category=cls.category_a1,
            name="Product A2",
            price=Decimal("50.00"),
            stock_quantity=0,
        )

    # ------------------------------------------------------------------
    # Category Model Tests
    # ------------------------------------------------------------------
    def test_category_creation_success(self):
        """Category can be created successfully."""
        cat = Category.objects.create(
            store=self.store_a,
            name="New Category",
        )
        self.assertIsNotNone(cat.pk)
        self.assertEqual(cat.store, self.store_a)
        self.assertEqual(cat.name, "New Category")

    def test_category_unique_name_per_store(self):
        """Duplicate category name within the same store raises ValidationError."""

        with self.assertRaises(ValidationError):
            Category.objects.create(
                store=self.store_a,
                name="Category A1",  # already exists
            )

    def test_category_same_name_different_store_allowed(self):
        """Same category name in a different store is allowed."""
        cat = Category.objects.create(
            store=self.store_b,
            name="Category A1",  # same name, different store
        )
        self.assertIsNotNone(cat.pk)

    # ------------------------------------------------------------------
    # Product Model Tests
    # ------------------------------------------------------------------
    def test_product_auto_sets_out_of_stock_on_save(self):
        """is_out_of_stock is automatically updated based on stock_quantity."""
        # Initially stock_quantity=5 should be False
        self.assertFalse(self.product_a1.is_out_of_stock)

        # Update stock_quantity to 0
        self.product_a1.stock_quantity = 0
        self.product_a1.save()
        self.product_a1.refresh_from_db()
        self.assertTrue(self.product_a1.is_out_of_stock)

        # Update stock_quantity to positive
        self.product_a1.stock_quantity = 3
        self.product_a1.save()
        self.product_a1.refresh_from_db()
        self.assertFalse(self.product_a1.is_out_of_stock)

    def test_product_discount_price_validation(self):
        """discount_price must be strictly less than price."""
        product = Product(
            store=self.store_a,
            category=self.category_a1,
            name="Invalid Discount",
            price=Decimal("50.00"),
            discount_price=Decimal("50.00"),  # equal
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

        product.discount_price = Decimal("60.00")  # greater
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_cost_price_validation(self):
        """cost_price must be strictly less than price."""
        product = Product(
            store=self.store_a,
            category=self.category_a1,
            name="Invalid Cost",
            price=Decimal("100.00"),
            cost_price=Decimal("100.00"),  # equal
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

        product.cost_price = Decimal("120.00")
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_cross_tenant_category_validation(self):
        """Product cannot be assigned a category from another store."""
        product = Product(
            store=self.store_a,
            category=self.category_b1,  # belongs to Store B
            name="Cross Tenant",
            price=Decimal("10.00"),
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_unique_name_per_category_per_store(self):
        """Duplicate product name in same category/store raises ValidationError."""

        with self.assertRaises(ValidationError):
            Product.objects.create(
                store=self.store_a,
                category=self.category_a1,
                name="Product A1",  # duplicate
                price=Decimal("99.00"),
            )

    def test_product_unique_sku_per_store(self):
        """Duplicate SKU within the same store raises ValidationError."""

        with self.assertRaises(ValidationError):
            Product.objects.create(
                store=self.store_a,
                category=self.category_a2,
                name="Another Product",
                sku="SKU-A1",  # duplicate
                price=Decimal("20.00"),
            )

    def test_product_same_sku_different_store_allowed(self):
        """Same SKU in different stores is allowed."""
        product = Product.objects.create(
            store=self.store_b,
            category=self.category_b1,
            name="Product with same SKU",
            sku="SKU-A1",  # same SKU as in Store A
            price=Decimal("30.00"),
        )
        self.assertIsNotNone(product.pk)

    # ------------------------------------------------------------------
    # ProductImage Model Tests
    # ------------------------------------------------------------------
    def test_product_image_cross_tenant_validation(self):
        """Image cannot be assigned to a product from a different store."""
        image = ProductImage(
            store=self.store_b,  # different from product's store
            product=self.product_a1,
            image=get_dummy_image("test.jpg"),
        )
        with self.assertRaises(ValidationError):
            image.full_clean()

    def test_product_image_primary_uniqueness_validation(self):
        """Only one primary image per product is allowed."""
        # Create first primary image
        primary_image = ProductImage.objects.create(
            store=self.store_a,
            product=self.product_a1,
            image=get_dummy_image("primary.jpg"),
            is_primary=True,
        )

        # Attempt to create another primary image for same product
        duplicate_primary = ProductImage(
            store=self.store_a,
            product=self.product_a1,
            image=get_dummy_image("secondary.jpg"),
            is_primary=True,
        )
        with self.assertRaises(ValidationError):
            duplicate_primary.full_clean()
