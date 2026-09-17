# Order Model

## Purpose

This document describes the order database architecture used in the Smart Commerce Platform.

The order model represents customer purchases and manages the relationship between customers, products, and store transactions.

---

# Overview

The order domain consists of two main entities:

- Order
- OrderItem

The Order model represents the overall customer purchase, while OrderItem represents individual products included within the order.

---

# Tenant Ownership

Orders belong to a single merchant store.

Ownership structure:

```text
Store
 |
 └── Orders
        |
        └── Order Items
```

Each order remains isolated within its owning store.

This ensures that order data cannot be accessed or modified across different merchant stores.

---

# Order Entity

Each order belongs to:

- One Store
- One Customer

The order stores the information required to represent a customer transaction.

Responsibilities include:

- Tracking customer purchases
- Maintaining order lifecycle state
- Preserving historical business records

---

# OrderItem Entity

Order items represent products included in an order.

Relationship:

```text
Order
 |
 └── Order Items
        |
        └── Product
```

Each order item belongs to:

- One Order
- One Product

Order items connect the order workflow with the product catalog.

---

# Product Relationship

Products are referenced through OrderItem instead of directly from Order.

This design allows:

- Multiple products per order
- Product quantity tracking
- Independent product management

The product domain remains separate from order processing.

---

# Inventory Synchronization

Order lifecycle events affect product quantities.

Current business rules include:

| Event | Effect |
|---|---|
| Add OrderItem | Decrease quantity |
| Remove OrderItem | Restore quantity |
| Cancel Order | Restore quantity |
| Restore Order | Apply quantity change |
| Delete Order | Restore quantity |

Inventory synchronization is handled through business logic outside the database relationship layer.

This keeps database relationships focused on data ownership while business logic manages inventory behavior.

---

# Soft Delete

Orders support soft deletion.

Deleted orders remain stored to preserve:

- Historical records
- Dashboard statistics
- Future reporting

Deleted orders are hidden from normal queries through the default manager.

This approach prevents permanent loss of important business information.

---

# OrderItem Deletion

Order items do not require independent historical preservation.

They can be permanently deleted when removed from an order.

This keeps the database clean while preserving important order history.

---

# Tenant Isolation

Order relationships must respect tenant ownership.

Rules include:

- Order and customer must belong to the same store.
- Order items can only reference products from the same store.
- Orders cannot access resources from another tenant.

These rules maintain data integrity and prevent cross-tenant access.

---

# Design Principles

The order model follows these principles:

- Business data preservation
- Tenant isolation
- Database normalization
- Clear entity responsibilities
- Scalability

---

# Future Evolution

Future improvements may include:

- Order status history
- Payment records
- Shipment tracking
- Order notes
- Customer order analytics

---

# Related Documentation

- `Database/customer-model.md`
- `Database/product-model.md`
- `Database/tenant-isolation.md`
- `Architecture/order-management.md`