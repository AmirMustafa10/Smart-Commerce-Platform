# Product Database Design

## Overview

The product catalog is designed to support a multi-tenant SaaS architecture.

Every business entity belongs to a single store.

---

## Category

Each category belongs to exactly one store.

Categories cannot be shared across stores.

---

## Product

Each product belongs to:

- One Store
- One Category

A validation rule ensures that both references belong to the same tenant.

This prevents cross-tenant relationships and guarantees data integrity.

---

## Pricing Strategy

Products store multiple prices.

| Field | Purpose |
|-------|---------|
| Cost Price | Internal purchasing cost |
| Price | Selling price |
| Discount Price | Promotional selling price |

Keeping these values separately simplifies:

- Profit calculation
- Reporting
- Promotions

---

## SKU

Every product owns a Stock Keeping Unit.

SKU is intended for:

- Inventory
- Product Search
- Barcode integration
- External systems

---

## Images

Images are stored in a separate model.

Relationship:

Product

↓

Many Images

Reasons:

- Unlimited images
- Cleaner Product model
- Better scalability

---

## Validation

Image uploads are validated using:

- File extension
- File size
- Pillow image verification