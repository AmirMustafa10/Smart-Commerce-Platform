# products/urls.py
from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # Category URLs
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "categories/create/", views.CategoryCreateView.as_view(), name="category_create"
    ),
    path(
        "categories/<uuid:pk>/update/",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<uuid:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    # Product URLs
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/create/", views.ProductCreateView.as_view(), name="product_create"),
    path(
        "products/<uuid:pk>/update/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "products/<uuid:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
]
