# Order Management

## Purpose

This document describes how order processing is organized within the Smart Commerce Platform.

It explains the responsibility of the order domain, the order lifecycle, business rules, and how orders interact with other business entities while preserving tenant isolation.

---

# Scope

This document covers:

- Order lifecycle
- Customer and order relationships
- Order item management
- Inventory synchronization rules
- Order status handling
- Business workflow

This document does **not** cover:

- Database schema details
- Django model implementation
- API endpoints
- Payment processing
- External integrations

---

# Overview

The Orders application manages the sales workflow between merchants and their customers.

Each order represents a customer purchase within a specific store and contains one or more order items referencing products from the same merchant catalog.

The order domain is responsible for coordinating the purchasing workflow while keeping product management and inventory data separated through clear business rules.

---

# Domain Responsibilities

The order domain is responsible for:

- Creating customer orders
- Managing order items
- Tracking order lifecycle changes
- Maintaining order history
- Synchronizing inventory changes
- Preserving historical business data

The application separates order processing from product management to maintain clear business boundaries and avoid coupling between different domains.

---

# Order Structure

The relationship between order entities is:

```text
Store
 |
 ├── Customer
 |
 └── Order
        |
        └── Order Items
                |
                └── Product
```

Business rules:

- Each order belongs to a single store.
- Each order belongs to a customer within the same store.
- Each order item represents a product included within the order.
- Products referenced by order items must belong to the same store as the order.

---

# Order Lifecycle

Orders follow a controlled lifecycle to ensure consistency between customer purchases, inventory quantities, and historical records.

## Supported States

Current supported order states include:

- Active orders
- Cancelled orders
- Restored orders
- Soft-deleted orders

The lifecycle rules ensure that inventory changes are applied correctly while preserving important business history.

---

# Inventory Synchronization

Inventory changes are handled through business rules triggered by order lifecycle events.

## Inventory Rules

| Event                  | Inventory Effect                |
| ---------------------- | ------------------------------- |
| Adding an order item   | Decreases product quantity      |
| Removing an order item | Restores product quantity       |
| Cancelling an order    | Restores product quantity       |
| Restoring an order     | Applies inventory changes again |
| Deleting an order      | Restores affected quantities    |

These rules are implemented through Django signals to keep inventory synchronization separate from the order models themselves.

This design keeps responsibilities separated between:

- Order management
- Product management
- Inventory control

---

# Soft Delete Strategy

Orders use soft deletion instead of permanent deletion.

Deleted orders remain stored to preserve:

- Historical records
- Dashboard statistics
- Business analysis
- Future reporting requirements

The system hides deleted orders from normal application workflows while maintaining access for internal operations when required.

This approach prevents accidental loss of important business information.

---

# Order Items

Order items represent the relationship between orders and products.

Each order item:

- Belongs to one order
- References one product
- Represents a purchased product entry

Order items do not require independent historical tracking because their business meaning depends on the parent order.

Therefore, order items can be permanently removed when they are no longer required.

---

# Tenant Isolation

Orders follow the platform tenant isolation strategy.

Business rules ensure that:

- Orders belong only to their owning store.
- Customers must belong to the same store as their orders.
- Order items cannot reference products from another store.

These rules prevent cross-tenant data access and preserve business integrity between different merchants.

---

# Design Principles

The order domain follows these principles:

- Separation of concerns
- Clear business boundaries
- Tenant isolation
- Historical data preservation
- Event-driven business rules
- Maintainable workflows

---

# Future Evolution

Future improvements may include:

- Customizable order status workflow
- Payment integration
- Shipment tracking
- Order notifications
- Customer order history
- Analytics and reporting
- WhatsApp order creation

---

# Related Documentation

- `Database/order-model.md`
- `Database/customer-model.md`
- `Database/tenant-isolation.md`
- `Architecture/product-management.md`
- `Development/testing-strategy.md`
