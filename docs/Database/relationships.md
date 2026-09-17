# Database Relationships

## Purpose

This document provides a high-level overview of the relationships between the primary database entities in the Smart Commerce Platform.

It explains how business entities are connected and how ownership is maintained across the platform.

---

# Overview

The database follows a relational design centered around the `Store` entity.

The Store represents the tenant boundary, while other business entities are connected through ownership relationships.

This structure provides clear data ownership, tenant isolation, and scalability.

---

# Entity Relationship Overview

The current database structure can be summarized as:

```text id="d1v7ma"
                    User
                     |
                     ▼
                  Store
      ┌────────────┼─────────────┐
      ▼            ▼             ▼
 Category      Product      Customer
      │            │             │
      │            ▼             ▼
      │      ProductImage      Order
      │                          │
      └──────────────────────────┤
                                 ▼
                            OrderItem
```

---

# Store Relationships

The Store is the central business entity.

Current relationships include:

| Related Model | Relationship                |
| ------------- | --------------------------- |
| User          | One Store → Many Users      |
| Category      | One Store → Many Categories |
| Product       | One Store → Many Products   |
| Customer      | One Store → Many Customers  |
| Order         | One Store → Many Orders     |

Future modules may extend this structure with:

- Inventory
- Suppliers
- Payments

---

# User Relationships

Users belong to a single Store.

Each user operates within the context of that store.

Different user roles determine responsibilities but do not change the ownership structure.

Relationship:

```text id="9u2hrj"
Store

 |

 └── Users
```

---

# Category Relationships

Each category belongs to exactly one Store.

Relationship:

```text id="zsnvuh"
Store

 |

 └── Categories
```

Categories cannot be shared between different merchants.

---

# Product Relationships

Each product belongs to:

- One Store
- One Category

Business validation ensures that the selected category belongs to the same store as the product.

Relationship:

```text id="8l3g2n"
Store
   |
   ├── Categories
   |
   └── Products
          |
          |
 Category Validation
```

---

# Product Image Relationships

Each product may contain multiple images.

Relationship:

```text id="2bzqvz"
Product

 |

 └── Product Images
```

The ProductImage model depends on the Product model and cannot exist independently.

---

## Customer Relationships

Each customer belongs to exactly one Store.

Customers may place multiple orders within their owning store.

Relationship:

```text
Store
   |
   └── Customers
          |
          └── Orders
```

Customers cannot be shared across different stores.

---

## Order Relationships

Each order belongs to:

- One Store
- One Customer

Each order contains one or more order items.

Relationship:

```text
Store
   |
   ├── Customers
   |
   └── Orders
          |
          └── Order Items
```

Business validation ensures that all referenced entities belong to the same tenant.

---

# Ownership Flow

Ownership flows from the Store down to all tenant-owned resources.

```text id="yc6tw7"
Store
   |
   ├── Users
   ├── Categories
   ├── Products
   │      |
   │      └── Product Images
   ├── Customers
   └── Orders
          |
          └── Order Items
```

This structure guarantees that every business resource belongs to a single tenant.

---

# Relationship Principles

The database relationships follow these principles:

- Every business resource has a clear owner.
- Tenant-owned resources cannot cross store boundaries.
- Parent-child relationships preserve data integrity.
- Business validation enforces ownership consistency.
- Related entities remain normalized.
- Orders may only reference customers belonging to the same store.
- Order items may only reference products owned by the same store.

---

# Future Evolution

As the platform grows, new business modules will extend the same ownership hierarchy.

Possible future relationships include:

```text id="p2rj0l"
Store
 |
 ├── Inventory
 ├── Suppliers
 ├── Payments
 ├── Notifications
 └── Analytics
```

These modules should follow the existing tenant ownership architecture to maintain consistency.

---

# Related Documentation

- `Database/database-overview.md`
- `Database/base-models.md`
- `Database/tenant-isolation.md`
- `Database/store-model.md`
- `Database/product-model.md`
