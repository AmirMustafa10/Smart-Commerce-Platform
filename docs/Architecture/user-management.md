# User Management

## Purpose

This document describes how users are managed throughout the Smart Commerce Platform.

It explains the user lifecycle, ownership model, internal staff management, and profile management while keeping authentication and authorization documented separately.

---

## Scope

This document covers:

- Merchant accounts
- Internal staff management
- User lifecycle
- Profile management
- Password management

This document does **not** cover:

- Authentication workflow
- Authorization rules
- Django Admin configuration
- Database implementation

---

## Overview

The platform distinguishes between business owners and internal staff members.

Merchants register publicly to create their business within the platform, while internal users are created and managed exclusively by the store owner.

This approach preserves tenant ownership and prevents unauthorized account creation.

---

# User Types

The platform currently supports multiple user types.

### Merchant

The merchant is the owner of the business and the primary administrator of the store.

The merchant is responsible for managing the business, creating internal users, and maintaining store configuration.

---

### Manager

Managers are internal staff members created by the store owner.

They are intended to assist with day-to-day business operations while remaining under the ownership of the merchant.

---

### Shipper

Shippers are internal users responsible for delivery-related operations.

Like all staff members, shipper accounts are created and managed by the store owner.

---

# User Lifecycle

The platform separates external registration from internal account creation.

Current lifecycle:

1. Merchant registers.
2. Store is created.
3. Merchant accesses the dashboard.
4. Merchant creates internal staff accounts.
5. Staff accounts may be activated or deactivated when necessary.

This workflow ensures that every internal account belongs to an existing business.

---

# Team Management

Store owners manage internal team members through dedicated management pages.

Current capabilities include:

- Creating staff accounts
- Viewing team members
- Activating accounts
- Deactivating accounts

Instead of deleting accounts, activation status is used to preserve historical relationships and business records.

---

# Profile Management

Authenticated users can manage their own account information.

Current capabilities include:

- Viewing profile information
- Updating personal details
- Changing account passwords

Each user manages their own profile, preventing unauthorized modifications by other users.

---

# Password Management

Password updates extend Django's built-in password management workflow.

This approach allows interface customization while preserving Django's proven authentication and security mechanisms.

---

# Design Principles

The user management system follows these architectural principles:

- Clear ownership hierarchy
- Tenant isolation
- Separation between public registration and internal user creation
- Data preservation through account activation
- Self-service profile management

---

# Future Evolution

Future enhancements may include:

- Invitation by email
- Role-based permission groups
- Audit logs
- Employee activity history
- User avatars
- Multi-factor authentication
- Employee onboarding workflow

---

# Related Documentation

- `Architecture/authentication-flow.md`
- `Architecture/authorization.md`
- `Architecture/store-management.md`
- `Architecture/application-routing.md`
- `ADR/ADR-001-custom-user-manager.md`
- `ADR/ADR-003-custom-user-model.md`
