# Database Overview

## Purpose

This document provides a high-level overview of the database architecture used in the Smart Commerce Platform.

It explains the general database design principles, entity organization, and relationship strategy across different business domains.

---

## Scope

This document covers:

- Database architecture overview
- Entity organization
- Domain relationships
- Data ownership principles

This document does **not** cover:

- Detailed model fields
- Migration history
- Query optimization
- Database deployment configuration

---

# Overview

The platform uses a relational database design based on Django's ORM.

The database structure is organized around business domains, where each Django application owns and manages its related entities.

The main domains currently include:

- Accounts
- Stores
- Products
- Orders
- Customers

The modular database architecture allows additional domains such as Inventory, Payments, Notifications, and Analytics to be introduced as the platform grows.

---

# Domain Organization

The database is organized around the following core entities:

```text
User
 |
 ▼
Store
 |
 ├──────────────┬───────────────┐
 ▼              ▼               ▼
Categories    Products      Customers
                 |               |
                 ▼               ▼
          Product Images      Orders
                                  |
                                  ▼
                             Order Items
```

The Store entity represents the ownership boundary for merchant-related data.
Current merchant-owned entities include categories, products, customers, and orders. Together, they represent the platform's primary business domains.

---

# Tenant-Based Data Ownership

The platform follows a tenant-aware database design.

Each merchant operates within an isolated business space represented by a Store.

Business entities that belong to merchants reference their owning Store to ensure:

- Data ownership clarity
- Tenant isolation
- Secure filtering
- Future scalability

---

# Database Design Principles

The database design follows these principles:

## Separation of Domains

Each application owns its business entities and related logic.

Examples:

- Accounts manages user identity.
- Stores manages merchant businesses.
- Products manages product catalog data.

---

## Data Integrity

Relationships between entities are designed to prevent invalid data connections.

Examples:

- Products must belong to a valid store.
- Categories must belong to the same store as their products.
- Orders must reference customers belonging to the same store.
- Order items must reference products owned by the same store.
- Tenant resources cannot cross business boundaries.

---

## Extensibility

The current database structure allows future modules to be introduced without major restructuring.

Possible future domains:

- Inventory
- Payments
- Notifications
- Analytics

---

# Future Evolution

Future database improvements may include:

- Advanced indexing strategies
- Database performance optimization
- Audit history tables
- Event tracking
- Data warehousing for analytics

---

# Related Documentation

- `Database/tenant-isolation.md`
- `Database/custom-user-model.md`
- `Database/store-model.md`
- `Database/product-model.md`
- `Database/relationships.md`
- `Architecture/project-structure.md`
- `Database/customer-model.md`
- `Database/order-model.md`
- `Architecture/order-management.md`
