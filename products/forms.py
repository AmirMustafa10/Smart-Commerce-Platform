from django import forms
from .models import Category, Product
from django.utils.translation import gettext_lazy as _


class CategoryForm(forms.ModelForm):
    """Form for creating and updating product categories."""

    class Meta:
        model = Category
        fields = ["name", "description", "is_active"]
        # store, is_deleted, sort_order are handled elsewhere or set automatically


class ProductForm(forms.ModelForm):
    """Form for creating and updating products with tenant isolation."""

    def __init__(self, *args, **kwargs):
        # Pop the store argument before calling super().__init__
        self.store = kwargs.pop("store", None)
        super().__init__(*args, **kwargs)

        # Restrict category choices to those belonging to the given store and active
        if self.store is not None:
            self.fields["category"].queryset = Category.objects.filter(
                store=self.store,
                is_active=True,
            )
        else:
            # If no store provided, show none to prevent mistakes
            self.fields["category"].queryset = Category.objects.none()

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "sku",
            "description",
            "price",
            "discount_price",
            "cost_price",
            "stock_quantity",
            "is_active",
        ]
        # store, is_out_of_stock, is_deleted are excluded
