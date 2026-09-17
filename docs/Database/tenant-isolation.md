# Tenant Data Isolation

## Purpose

This document describes the tenant isolation strategy used in the Smart Commerce Platform.

The main goal is to ensure that every merchant can only access and manage resources belonging to their own store while preserving data integrity, historical records, and future scalability.

---

# Overview

The platform follows a tenant-aware data architecture.

Each merchant operates within an isolated business environment represented by a `Store` entity.

All business entities that belong to a merchant must maintain a clear ownership relationship with their store.

This prevents cross-tenant data leakage and ensures that business data remains isolated between merchants.

---

# Ownership Model

The platform follows the following ownership hierarchy:

```text
User
 |
 ▼
Store
 |
 ├────────────┬────────────┬────────────┐
 ▼            ▼            ▼            ▼
Category   Product     Customer      Team Member
                |            |
                ▼            ▼
         ProductImage     Order
                               |
                               ▼
                          OrderItem
```

The `Store` entity represents the tenant boundary for all merchant-owned resources.

---

# Tenant Ownership Rules

Current ownership relationships include:

```text
User → Store

Staff → Store

Category → Store

Product → Store

Customer → Store

Order → Store

Order → Customer

OrderItem → Order

OrderItem → Product

Product → Category
```

Business rules ensure that related entities cannot reference resources belonging to another store.

Examples:

- A product from Store A cannot use a category from Store B.
- A user from one store cannot access another store's resources.
- Team members belong only to their assigned store.
- A customer from Store A cannot be assigned to an order belonging to Store B.
- An order item cannot reference a product owned by another store.

---

# Base Model Architecture

The project uses shared abstract models to centralize common database behavior.

The inheritance structure is:

```text
BaseModel
    |
    ▼
TenantAwareModel
    |
    ├──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼
Product    Category   Customer    Order
```

---

# BaseModel

`BaseModel` contains fields and behaviors shared across multiple database entities.

Current responsibilities include:

- Creation timestamp
- Update timestamp
- Soft deletion support

Common fields include:

- `created_at`
- `updated_at`
- `is_deleted`
- `deleted_at`

This approach prevents repeating common fields across multiple models and keeps the database design consistent.

---

# TenantAwareModel

`TenantAwareModel` extends `BaseModel` and adds tenant ownership support.

Models that belong to a merchant inherit from this abstract model.

Benefits include:

- Centralized store ownership
- Reduced duplicated code
- Consistent tenant relationships
- Easier future modifications

---

# Data Isolation Strategy

Tenant isolation is enforced through multiple layers.

## Relationship Layer

Database relationships maintain ownership boundaries.

Examples:

- Products belong to a specific store.
- Categories belong to a specific store.
- Customers belong to a specific store.
- Orders belong to a specific store.
- Product categories must belong to the same store as the product.
- Orders may only reference customers belonging to the same store.
- Order items may only reference products owned by the same store.

---

## Application Layer

Application logic must always filter tenant-owned data according to the authenticated user's store.

This ensures that queries only return resources belonging to the current tenant.

---

## Authorization Layer

Authorization rules prevent users from performing actions outside their responsibilities.

Examples:

- Store owners manage their own business.
- Managers operate within their assigned store.
- Users cannot access another tenant's resources.

---

# Soft Delete Strategy

The platform uses soft deletion instead of permanent deletion.

Instead of removing records from the database, the system marks them as deleted while preserving the original data.

Each soft-deleted record contains:

- `is_deleted` to indicate deletion status.
- `deleted_at` to record when deletion occurred.

Current implementation applies soft deletion to business entities that require historical preservation, such as orders.

Supporting entities that do not require historical retention, such as order items, may be permanently deleted when appropriate.

---

# Soft Delete Managers

The project uses multiple managers to control deleted record visibility.

## Default Manager

The default manager hides deleted records from normal application queries.

Example:

```python
objects
```

This ensures that deleted records do not accidentally appear in normal application workflows.

---

## All Objects Manager

A secondary manager provides access to all records, including soft-deleted records.

Example:

```python
all_objects
```

This is intended for:

- Administrative operations
- Data recovery
- Auditing
- Internal maintenance

---

# Design Principles

The tenant isolation strategy follows these principles:

- Explicit data ownership
- Strong tenant boundaries
- Default protection against deleted records
- Historical data preservation
- Reusable database abstractions
- Future scalability

---

# Future Evolution

Future improvements may include:

- Automated tenant filtering middleware
- Database-level row security
- Audit history tracking
- Restore workflows
- Data retention policies
- Advanced tenant management tools

---

# Related Documentation

- `Database/database-overview.md`
- `Database/base-models.md`
- `Database/custom-user-model.md`
- `Database/store-model.md`
- `Database/product-model.md`
- `Architecture/authorization.md`
