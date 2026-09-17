# Customer Model

## Purpose

This document describes the customer database architecture used in the Smart Commerce Platform.

The customer model represents merchant customers and provides the foundation for customer-related business operations within the platform.

---

# Overview

Customers are independent business entities separate from platform users.

A customer represents a person or organization that purchases products from a merchant store.

The separation between users and customers allows the platform to distinguish between:

- System users who operate the platform.
- Business customers who interact with merchants.

---

# Tenant Ownership

Customers belong to a single merchant store.

Ownership structure:

```text
Store
 |
 └── Customers
```

Each customer is isolated within its owning store.

Customers cannot be shared between different merchants.

---

# Customer Responsibilities

The Customer model is responsible for storing business customer information.

Current responsibilities include:

- Customer identity information
- Customer contact information
- Store ownership reference
- Association with customer orders

---

# Customer and User Separation

Customers are not authentication users.

The relationship is:

```text
System Users

Owner
Manager
Shipper


Business Customers

Customer
```

This separation prevents mixing internal platform accounts with external business entities.

It also keeps authentication responsibilities separate from business customer management.

---

# Customer Relationships

A customer may have multiple orders.

Relationship:

```text
Customer
 |
 └── Orders
```

Each order belongs to exactly one customer.

This relationship allows the platform to track customer purchasing history while maintaining proper data ownership.

---

# Tenant Isolation

Customer data follows the platform tenant isolation strategy.

Business rules ensure that:

- Customers belong only to their assigned store.
- Orders cannot reference customers from another store.
- Customer data cannot cross tenant boundaries.

These rules preserve merchant data privacy and prevent unauthorized access between different stores.

---

# Design Principles

The customer model follows these principles:

- Clear business entity separation
- Tenant isolation
- Data ownership consistency
- Scalability
- Maintainability

---

# Future Evolution

Future improvements may include:

- Customer addresses
- Customer segmentation
- Customer analytics
- Customer communication history
- Customer loyalty features

---

# Related Documentation

- `Database/store-model.md`
- `Database/order-model.md`
- `Database/tenant-isolation.md`
- `Architecture/order-management.md`