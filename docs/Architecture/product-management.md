# Product Management

## Purpose

This document describes how products are organized and managed within the Smart Commerce Platform.

It focuses on the business structure of the product catalog, the responsibilities of the product domain, and the architectural principles behind its design.

---

## Scope

This document covers:

- Product organization
- Category management
- Product pricing
- Product images
- Product validation
- Product administration

This document does **not** cover:

- Database schema
- Django model implementation
- API endpoints
- Order processing
- Inventory synchronization implementation

---

## Overview

The Products application is responsible for managing each merchant's product catalog.

Every store maintains an independent collection of categories, products, pricing, and product images while preserving complete tenant isolation across the platform.

The application is designed to remain extensible as additional inventory and commerce features are introduced.

---

# Product Organization

Products are organized into categories.

Each category belongs to a single store, and products may only reference categories owned by the same store.

This design prevents cross-tenant relationships and preserves data isolation between merchants.

---

## Product Usage

Products serve as the primary items sold through the platform.

They are referenced by customer orders while remaining independent of the order management domain.

Inventory quantities are automatically synchronized during order lifecycle events through business rules implemented outside the product domain.

This separation allows the product catalog to remain focused on product management while order processing handles inventory updates.

---

# Pricing Strategy

Each product maintains multiple pricing values to support different business needs.

| Field          | Purpose                   |
| -------------- | ------------------------- |
| Cost Price     | Internal purchasing cost  |
| Selling Price  | Customer selling price    |
| Discount Price | Promotional selling price |

Separating these values enables future profitability reporting, analytics, and pricing strategies without changing the underlying product structure.

---

# Product Identification

Each product is identified by a Stock Keeping Unit (SKU).

The SKU provides a stable business identifier that simplifies inventory management and supports future integrations such as barcode systems, warehouse management, and external sales channels.

---

# Product Images

Products support multiple images rather than a single image.

This design allows merchants to present products more effectively while keeping image management independent from the product entity itself.

Uploaded images are validated before storage to ensure only valid image files are accepted.

---

# Validation Strategy

Product validation follows a layered approach to improve data quality and system reliability.

Current validation includes:

- Category ownership validation
- File extension validation
- Image size validation
- Image integrity verification using Pillow

These validation layers help prevent invalid relationships and reduce the risk of storing unsupported or malicious files.

---

# Current Capabilities

- Creating products
- Updating products
- Deleting products
- Managing product categories
- Uploading multiple product images
- Product image validation
- Product pricing management
- Integration with the order management workflow
- Django Admin management

---

# Design Principles

The product domain follows these architectural principles:

- Tenant isolation
- Separation of concerns
- Domain-driven organization
- Clean validation boundaries
- Extensibility
- Scalability

The application is designed so that future inventory features can be introduced without requiring significant changes to the existing product structure.

---

# Future Evolution

Future enhancements may include:

- Product variants
- Barcode generation
- Stock movement history
- Bulk product import/export
- AI-assisted product categorization
- AI-powered product recommendations
- WhatsApp product synchronization
- Inventory forecasting

---

# Related Documentation

- `Architecture/project-structure.md`
- `Architecture/application-routing.md`
- `Database/product-model.md`
- `Database/tenant-isolation.md`
- `ADR/ADR-003-product-images.md`
- `Architecture/order-management.md`
- `Database/order-model.md`