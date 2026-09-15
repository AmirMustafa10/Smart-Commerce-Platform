# Product Model

## Purpose

This document describes the product database architecture used in the Smart Commerce Platform.

The product module is designed to support a multi-tenant SaaS environment while maintaining data integrity, scalability, and business flexibility.

---

# Overview

The product catalog is organized around three primary entities:

- Category
- Product
- ProductImage

Each entity has a dedicated responsibility, keeping the database structure normalized and maintainable.

All tenant-owned entities inherit from `TenantAwareModel`.

---

# Tenant Ownership

Products and categories belong to a single merchant store.

This ensures complete tenant isolation across the platform.

Ownership structure:

```text
Store
   |
   ├── Categories
   |
   └── Products
```

Tenant ownership prevents business data from being shared across merchants.

---

# Category

Categories organize products within a merchant's catalog.

Each category belongs to exactly one store.

Categories cannot be shared between different merchants.

Responsibilities include:

- Product organization
- Catalog structure
- Tenant ownership

---

# Product

Each product belongs to:

- One Store
- One Category

Business validation ensures that the selected category belongs to the same store as the product.

This prevents invalid cross-tenant relationships and preserves database consistency.

---

# Pricing Strategy

The platform stores multiple pricing values for each product.

| Field            | Purpose                   |
| ---------------- | ------------------------- |
| `cost_price`     | Internal purchasing cost  |
| `price`          | Standard selling price    |
| `discount_price` | Promotional selling price |

Separating these values supports:

- Profit calculations
- Financial reporting
- Promotional campaigns
- Dashboard analytics

---

# Stock Management

Each product maintains inventory-related information.

Current fields include:

- SKU (Stock Keeping Unit)
- Out-of-stock status

The SKU provides a stable business identifier suitable for:

- Inventory management
- Product search
- Barcode integration
- External systems

The `is_out_of_stock` field allows the application to distinguish product availability without removing products from the catalog.

---

# Product Images

Product images are stored in a dedicated model instead of the Product model.

Relationship:

```text
Product
    |
    ▼
ProductImage (One-to-Many)
```

This design supports:

- Multiple product images
- Better normalization
- Cleaner product model
- Easier future expansion

Image management within Django Admin is simplified through inline administration.

---

# Image Validation

Uploaded images are validated before storage.

Current validation includes:

- Allowed file extensions
- Maximum file size
- Pillow image verification

These validations help prevent invalid uploads while ensuring uploaded files are legitimate images.

---

# Administration

Products are managed through a customized Django Admin interface.

Current administrative features include:

- Product administration
- Category administration
- Inline product image management

Using `ProductImageInline` allows administrators to manage product images directly from the Product editing page.

---

# Design Principles

The product database follows these principles:

- Tenant isolation
- Database normalization
- Separation of concerns
- Business rule validation
- Scalability
- Maintainability

---

# Future Evolution

Possible future improvements include:

- Inventory transactions
- Product variants
- Brand management
- Supplier relationships
- Product attributes
- Barcode generation
- Multiple warehouse support

---

# Related Documentation

- `Database/base-models.md`
- `Database/tenant-isolation.md`
- `Architecture/product-management.md`
- `ADR/ADR-003-product-images.md`
- `Architecture/administration.md`
