# Base Models

## Purpose

This document describes the shared abstract database models used across the Smart Commerce Platform.

It explains how common database behavior is centralized and how model inheritance improves consistency, maintainability, and scalability across different business domains.

---

# Overview

The platform uses abstract base models to provide reusable database behavior across multiple entities.

Instead of repeating common fields and logic in every model, shared functionality is defined once and inherited where required.

This approach follows the DRY (Don't Repeat Yourself) principle and creates a consistent database structure across the application.

---

# Base Model Architecture

The project separates common model behavior into different abstraction levels.

The current inheritance structure is:

```text
                         BaseModel
                             |
             --------------------------------
             |                              |
           Store                 TenantAwareModel
                                            |
                              -------------------------
                              |                       |
                           Product                Category
```

---

# BaseModel

`BaseModel` is the foundation for database entities that require common lifecycle behavior.

It contains functionality that is shared across multiple models regardless of their business ownership.

---

## Responsibilities

Current responsibilities include:

* Creation tracking
* Update tracking
* Soft deletion support

Common fields include:

| Field        | Purpose                                            |
| ------------ | -------------------------------------------------- |
| `created_at` | Stores the creation timestamp                      |
| `updated_at` | Stores the last modification timestamp             |
| `is_deleted` | Indicates whether the record has been soft deleted |
| `deleted_at` | Stores the deletion timestamp                      |

---

# Why BaseModel Exists

Many entities require the same lifecycle information.

Without a shared base model, these fields would need to be duplicated across multiple database tables.

This creates several problems:

* Repeated code
* Inconsistent implementations
* More difficult maintenance
* Higher risk when adding future changes

By centralizing these behaviors, changes can be introduced in one place and applied consistently.

---

# Store Relationship With BaseModel

The `Store` model inherits directly from `BaseModel`.

This is intentional because the Store represents the tenant root entity.

The Store:

* Has its own lifecycle.
* Requires timestamps.
* Supports soft deletion.
* Does not belong to another Store.

Therefore, it should not inherit from `TenantAwareModel`.

---

# TenantAwareModel

`TenantAwareModel` extends `BaseModel` and introduces tenant ownership behavior.

It is used by entities that exist inside a merchant's store.

These models contain a relationship to the owning Store.

---

## Responsibilities

`TenantAwareModel` provides:

* Store ownership relationship
* Shared lifecycle behavior from `BaseModel`

Models using this abstraction automatically follow the tenant ownership structure.

Examples:

* Product
* Category
* Future tenant-owned entities

---

# Soft Delete Strategy

The platform uses soft deletion instead of permanently removing records.

When a record is deleted:

* The database row remains.
* The deletion state changes.
* The deletion timestamp is recorded.

This preserves:

* Historical information
* Business relationships
* Recovery possibilities
* Future auditing capabilities

---

# Soft Delete Fields

## is_deleted

A boolean flag that indicates whether the record is considered deleted.

Example:

```python
is_deleted = False
```

means the record is active.

```python
is_deleted = True
```

means the record has been deleted.

---

## deleted_at

Stores the exact time when the deletion occurred.

This provides additional information for:

* Auditing
* Recovery workflows
* Data retention policies

---

# Design Benefits

Using abstract base models provides:

## Consistency

All models share the same lifecycle behavior.

## Maintainability

Future changes can be applied centrally.

Example:

Adding a new shared field such as:

```python
created_by
```

can be done once instead of updating multiple models.

## Scalability

New business domains can reuse existing architecture.

Example:

Future models such as:

* Order
* Customer
* Inventory
* Supplier

can inherit from `TenantAwareModel` if they belong to a store.

---

# Design Principles

The base model architecture follows these principles:

* DRY (Don't Repeat Yourself)
* Separation of concerns
* Explicit ownership boundaries
* Reusable abstractions
* Long-term maintainability

---

# Future Evolution

Potential future additions may include:

* Created by user tracking
* Updated by user tracking
* Audit history
* Version tracking
* Common status management

Any future additions should represent truly shared behavior before being added to the base layer.

---

# Related Documentation

* `Database/database-overview.md`
* `Database/tenant-isolation.md`
* `Database/custom-user-model.md`
* `Database/store-model.md`
* `Database/product-model.md`
* `Architecture/store-management.md`
