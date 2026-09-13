from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from .models import Category, Product
from .forms import CategoryForm, ProductForm


class TenantQuerySetMixin:
    """
    Mixin to filter queryset based on the current user's store and exclude soft-deleted records.
    Must be used with LoginRequiredMixin to ensure user is authenticated.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(store=self.request.user.store, is_deleted=False)


class StoreManagerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to restrict access to Store Owners and Managers only.
    Shippers or other roles will get a 403 Forbidden error.
    """

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role in ["OWNER", "MANAGER"]


# ----------------------------------------------------------------------
# Category Views
# ----------------------------------------------------------------------


class CategoryListView(
    LoginRequiredMixin, TenantQuerySetMixin, StoreManagerRequiredMixin, ListView
):
    model = Category
    template_name = "products/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixin, StoreManagerRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "products/category_form.html"
    success_url = reverse_lazy("products:category_list")

    def get_form_kwargs(self):
        """
        Assign the store automatically
        """
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = Category(store=self.request.user.store)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add"
        context["btn_text"] = "Create Category"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully.")
        return super().form_valid(form)


class CategoryUpdateView(
    LoginRequiredMixin, TenantQuerySetMixin, StoreManagerRequiredMixin, UpdateView
):
    model = Category
    form_class = CategoryForm
    template_name = "products/category_form.html"
    success_url = reverse_lazy("products:category_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit"
        context["btn_text"] = "Save Changes"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully.")
        return super().form_valid(form)


class CategoryDeleteView(
    LoginRequiredMixin, TenantQuerySetMixin, StoreManagerRequiredMixin, DeleteView
):
    model = Category
    template_name = "products/category_confirm_delete.html"
    success_url = reverse_lazy("products:category_list")

    def form_valid(self, form):
        success_url = self.get_success_url()

        # Soft delete: set is_deleted flag instead of actual deletion
        self.object.is_deleted = True
        self.object.save(update_fields=["is_deleted"])

        messages.success(self.request, "Category deleted successfully.")
        return HttpResponseRedirect(success_url)


# ----------------------------------------------------------------------
# Product Views
# ----------------------------------------------------------------------


class ProductListView(
    LoginRequiredMixin, TenantQuerySetMixin, StoreManagerRequiredMixin, ListView
):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        base_qs = self.get_queryset()

        context["active_products_count"] = base_qs.filter(is_active=True).count()

        context["in_stock_products_count"] = base_qs.filter(
            stock_quantity__gt=0
        ).count()

        context["total_products_count"] = base_qs.count()

        return context


class ProductCreateView(LoginRequiredMixin, StoreManagerRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:product_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["store"] = self.request.user.store
        kwargs["instance"] = Product(store=self.request.user.store)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(
            store=self.request.user.store, is_active=True, is_deleted=False
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Product created successfully.")
        return super().form_valid(form)


class ProductUpdateView(
    LoginRequiredMixin, TenantQuerySetMixin, StoreManagerRequiredMixin, UpdateView
):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:product_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["store"] = self.request.user.store
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(
            store=self.request.user.store, is_active=True, is_deleted=False
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully.")
        return super().form_valid(form)


class ProductDeleteView(
    LoginRequiredMixin, TenantQuerySetMixin, StoreManagerRequiredMixin, DeleteView
):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("products:product_list")

    def form_valid(self, form):
        success_url = self.get_success_url()

        # Soft delete: set is_deleted flag instead of actual deletion
        self.object.is_deleted = True
        self.object.save(update_fields=["is_deleted"])

        messages.success(self.request, "Product deleted successfully.")
        return HttpResponseRedirect(success_url)
