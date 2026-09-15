# Authorization

## Purpose

This document describes the authorization strategy used in the Smart Commerce Platform.

It explains how access control is organized across different user types and how permissions are aligned with business ownership and responsibilities.

---

## Scope

This document covers:

* User roles
* Access boundaries
* Store ownership rules
* Internal staff permissions

This document does **not** cover:

* Authentication workflow
* User creation process
* Database implementation
* Django permission implementation details

---

# Overview

Authorization in the platform is based on business ownership and user responsibilities.

The system does not treat all authenticated users equally. Instead, each user type receives access according to their role within the merchant organization.

The main goal is to ensure that users can only access and modify resources that belong to their responsibilities.

---

# Ownership Model

Each merchant owns a store, and the store acts as the ownership boundary for tenant data.

The ownership hierarchy is:

```text
Merchant Owner

        |

        ▼

      Store

        |

 ┌──────┼────────┐

 ▼      ▼        ▼

Products Categories Team
```

All tenant-owned resources must belong to a specific store.

---

# User Roles and Responsibilities

## Store Owner

The store owner is the primary administrator of the business.

### Allowed Actions

* Manage store information
* Update store settings
* Activate or deactivate the store
* Create internal staff accounts
* Activate or deactivate staff accounts
* Manage products
* Manage categories
* Access owner dashboard

### Restricted Actions

The owner cannot bypass platform-level administration rules.

System administration remains separate from merchant ownership.

---

## Manager

Managers are internal users created by the store owner.

They assist with daily business operations.

### Allowed Actions

* Manage products
* Manage categories
* Update personal profile
* Change personal password

### Restricted Actions

Managers cannot:

* Modify store settings
* Manage team members
* Activate or deactivate staff accounts
* Manage store ownership

---

## Shipper

Shippers represent operational users responsible for delivery-related tasks.

Currently, shipper functionality is limited.

Future responsibilities may include:

* Managing assigned deliveries
* Updating shipment status
* Accessing delivery information

---

# Permission Boundaries

The platform follows the principle of least privilege.

Each user receives only the access required to perform their responsibilities.

Examples:

* A manager can manage products but cannot manage employees.
* A shipper can handle operational tasks but cannot access business configuration.
* A store owner manages the tenant but does not represent system administration.

---

# Tenant Isolation

Authorization works together with tenant isolation to protect merchant data.

A user should only access resources that belong to their own store.

Examples:

* A merchant cannot view another merchant's products.
* A manager cannot modify another store's categories.
* Team management is limited to the owning store.

---

# Design Principles

The authorization strategy follows these principles:

* Least Privilege
* Clear ownership boundaries
* Separation between platform administration and merchant administration
* Tenant data protection
* Role-based access control

---

# Future Evolution

As the platform grows, authorization may evolve to support more granular permissions.

Possible improvements include:

* Django Groups and Permissions
* Custom permission classes
* Object-level permissions
* Feature-based permissions
* Audit logs
* Permission management interface

---

# Related Documentation

* `Architecture/authentication-flow.md`
* `Architecture/user-management.md`
* `Architecture/store-management.md`
* `Database/tenant-isolation.md`
* `Architecture/administration.md`
