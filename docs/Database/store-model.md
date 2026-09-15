# Store Model

## Purpose

The `Store` model represents a merchant business within the Smart Commerce Platform.

Each merchant operates through a dedicated store, which acts as the tenant boundary for all business-related data.

The Store entity is the root of merchant ownership and provides the context for tenant-aware resources such as products, categories, and future business modules.

---

# Overview

The Store model represents the business identity of a merchant inside the platform.

Instead of attaching business data directly to users, the platform uses Store as the ownership root.

This design allows multiple users to operate within the same business while maintaining clear ownership boundaries.

---

# Design Decision

## Why Store Is the Tenant Root?

The Store represents the business itself, while users represent people who access and manage that business.

The relationship is:

```text id="7l8d2m"
Store

 |

 ├───────────────┐

 ▼               ▼

Users          Business Resources
                |
                |
        Products / Categories / Orders
```

This allows future expansion where multiple users can work inside the same merchant account.

---

# Base Model Relationship

The Store model inherits directly from `BaseModel`.

It does not inherit from `TenantAwareModel`.

Reason:

`TenantAwareModel` is designed for resources that belong to a store, while the Store itself represents the tenant boundary.

Correct structure:

```text id="2z3j3x"
BaseModel
    |
    ├── Store
    |
    └── TenantAwareModel
             |
             ├── Product
             └── Category
```

This prevents an incorrect ownership relationship where a store would require another store as its owner.

---

# Responsibilities

The Store model is responsible for:

- Store identity
- Merchant business information
- WhatsApp contact information
- Tenant ownership reference
- Store lifecycle management

---

# WhatsApp Contact Validation

The platform stores merchant WhatsApp contact information as part of the business identity.

The phone number field uses validation rules to ensure that stored numbers follow the expected format.

This prevents invalid contact information from being saved.

---

# Relationships

The Store model is connected to multiple parts of the system.

Current relationships include:

```text id="l54t9p"
Store

 |

 ├── Users

 ├── Categories

 ├── Products

 └── Team Members
```

Future tenant-owned resources may include:

- Customers
- Orders
- Inventory
- Payments
- Notifications

These resources should use the tenant ownership pattern provided by `TenantAwareModel`.

---

# Store Lifecycle

The Store supports controlled lifecycle management.

Instead of permanently removing stores, the platform uses activation and deactivation.

Benefits include:

- Preserving historical data
- Maintaining relationships
- Supporting future recovery
- Avoiding data integrity issues

Soft deletion support is provided through `BaseModel`.

---

# Administration

The Store model has a dedicated Django Admin configuration.

The admin interface provides better management and visibility for store data.

Administrative capabilities include:

- Viewing store information
- Managing store records
- Monitoring store status

Merchant-facing store management remains separated through dedicated application views.

---

# Design Benefits

The Store-centered design provides:

- Clear tenant boundaries
- Better SaaS scalability
- Support for multiple users per business
- Improved data isolation
- Easier future expansion

---

# Future Evolution

Possible future improvements include:

- Store analytics
- Business activity tracking
- Tenant-level reporting
- Store audit history
- Subscription management

---

# Related Documentation

- `Database/base-models.md`
- `Database/tenant-isolation.md`
- `Database/custom-user-model.md`
- `Architecture/authorization.md`
- `Architecture/store-management.md`
