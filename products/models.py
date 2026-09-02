import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from stores.models import TenantAwareModel


def validate_image_size(image):
    """Ensure uploaded image does not exceed 2MB."""
    max_size_mb = 2
    max_size_bytes = max_size_mb * 1024 * 1024
    if image.size > max_size_bytes:
        raise ValidationError(
            _(f"Image file too large. Maximum allowed size is {max_size_mb}MB.")
        )


def product_image_upload_path(instance, filename):
    """
    Upload path for product images:
    stores/<store_id>/products/<product_id>/<filename>
    """
    store_id = getattr(instance, "store_id", "unknown")
    product_id = getattr(instance, "product_id", "unknown")
    return f"stores/{store_id}/products/{product_id}/{filename}"


class Category(TenantAwareModel):
    """Product category belonging to a specific store (tenant)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the category."),
    )
    name = models.CharField(_("name"), max_length=100, help_text=_("Category name."))
    description = models.TextField(
        _("description"), blank=True, default="", help_text=_("Optional description.")
    )
    is_active = models.BooleanField(
        _("active"), default=True, help_text=_("Visibility flag for customers.")
    )
    sort_order = models.IntegerField(
        _("sort order"), default=0, help_text=_("Display order.")
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["store", "sort_order"]),
            models.Index(fields=["store", "name"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Normalize name and validate."""
        super().clean()
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError({"name": _("Name cannot be blank.")})


class Product(TenantAwareModel):
    """Product belonging to a specific store (tenant)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the product."),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        help_text=_("Category this product belongs to."),
    )
    name = models.CharField(_("name"), max_length=200, help_text=_("Product name."))
    sku = models.CharField(
        _("SKU"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Stock Keeping Unit / Barcode (optional, unique per store)."),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Optional product description."),
    )
    cost_price = models.DecimalField(
        _("cost price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Internal cost price (optional)."),
    )
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Regular selling price (must be > 0)."),
    )
    discount_price = models.DecimalField(
        _("discount price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Discounted price (optional, must be < price)."),
    )
    is_active = models.BooleanField(
        _("active"), default=True, help_text=_("Visibility flag for customers.")
    )
    is_out_of_stock = models.BooleanField(
        _("out of stock"),
        default=False,
        help_text=_("If True, show 'Out of Stock' in UI."),
    )
    sort_order = models.IntegerField(
        _("sort order"), default=0, help_text=_("Display order within category.")
    )

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["store", "category"]),
            models.Index(fields=["store", "is_active"]),
            models.Index(fields=["store", "sort_order"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["store", "sku"],
                name="unique_sku_per_store",
                condition=~models.Q(sku=None),  # enforce only when sku is not null
            )
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate product data and enforce tenant isolation."""
        super().clean()  # ensures store is set

        # Normalize name
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError({"name": _("Name cannot be blank.")})

        # Normalize SKU (strip whitespace, treat empty as None)
        if self.sku is not None:
            self.sku = self.sku.strip()
            if not self.sku:
                self.sku = None

        # Validate price > 0
        if self.price is not None and self.price <= Decimal("0.00"):
            raise ValidationError({"price": _("Price must be greater than zero.")})

        # Validate discount_price < price
        if self.discount_price is not None:
            if self.discount_price < Decimal("0.00"):
                raise ValidationError(
                    {"discount_price": _("Discount price cannot be negative.")}
                )
            if self.price is not None and self.discount_price >= self.price:
                raise ValidationError(
                    {
                        "discount_price": _(
                            "Discount price must be less than the regular price."
                        )
                    }
                )

        # Validate cost_price < price
        if self.cost_price is not None:
            if self.cost_price < Decimal("0.00"):
                raise ValidationError(
                    {"cost_price": _("Cost price cannot be negative.")}
                )
            if self.price is not None and self.cost_price >= self.price:
                raise ValidationError(
                    {"cost_price": _("Cost price must be less than the regular price.")}
                )

        # Tenant isolation: category.store must equal product.store
        if self.category_id and self.store_id:
            if self.category.store_id != self.store_id:
                raise ValidationError(
                    {"category": _("Selected category does not belong to this store.")}
                )


class ProductImage(TenantAwareModel):
    """Image associated with a product."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the image."),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        help_text=_("Product this image belongs to."),
    )
    image = models.ImageField(
        _("image"),
        upload_to=product_image_upload_path,
        validators=[
            validate_image_size,
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
        ],
        help_text=_("Product image file (max 2MB, formats: JPG, JPEG, PNG, WEBP)."),
    )
    is_primary = models.BooleanField(
        _("primary"), default=False, help_text=_("Mark as the main catalog image.")
    )
    sort_order = models.IntegerField(
        _("sort order"), default=0, help_text=_("Display order among images.")
    )

    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["product", "is_primary"]),
        ]

    def __str__(self):
        return f"Image for {self.product} ({self.id})"

    def clean(self):
        """Validate tenant isolation and ensure primary image integrity."""
        super().clean()

        # Tenant isolation: product.store must equal image.store
        if self.product_id and self.store_id:
            if self.product.store_id != self.store_id:
                raise ValidationError(
                    {"product": _("Selected product does not belong to this store.")}
                )

        # If is_primary is True, ensure no other primary exists for the same product
        if self.is_primary and self.product_id:
            existing_primary = (
                ProductImage.objects.filter(product_id=self.product_id, is_primary=True)
                .exclude(pk=self.pk)
                .exists()
            )
            if existing_primary:
                raise ValidationError(
                    {
                        "is_primary": _(
                            "Another image is already marked as primary for this product."
                        )
                    }
                )

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        If this image is set as primary, unset all other primary images for the same product
        before saving, in a transaction to ensure consistency.
        """
        if self.is_primary and self.product_id:
            ProductImage.objects.filter(
                product_id=self.product_id, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)
