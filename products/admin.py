# products/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, ProductImage


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "is_active", "sort_order", "created_at")
    list_filter = ("store", "is_active", "is_deleted")
    search_fields = ("name", "store__name")
    ordering = ("store", "sort_order")
    readonly_fields = ("created_at", "updated_at")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "is_primary", "sort_order")
    # Exclude store; we will assign it automatically in the parent's save_formset
    exclude = ("store",)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "store",
        "category",
        "sku",
        "price",
        "is_active",
        "is_out_of_stock",
    )
    list_filter = ("store", "category", "is_active", "is_out_of_stock", "is_deleted")
    search_fields = ("name", "sku", "store__name", "category__name")
    inlines = [ProductImageInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("Basic Info"),
            {"fields": ("store", "name", "category", "sku", "description")},
        ),
        (_("Pricing"), {"fields": ("cost_price", "price", "discount_price")}),
        (
            _("Status"),
            {
                "fields": (
                    "is_active",
                    "is_out_of_stock",
                    "is_deleted",
                    "stock_quantity",
                )
            },
        ),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )

    def save_formset(self, request, form, formset, change):
        """
        Ensure that each ProductImage inherits the store from the parent Product.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if hasattr(instance, "store_id") and not instance.store_id:
                instance.store = form.instance.store
            instance.save()
        formset.save_m2m()


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
