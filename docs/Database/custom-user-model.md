# User Model

## Purpose

This document describes the custom user model architecture used in the Smart Commerce Platform.

The user model represents authentication identity across the platform and is designed to support merchant accounts, internal team members, and future role expansion.

---

# Overview

The platform uses a custom Django User model instead of Django's default user implementation.

The custom model was introduced to support business requirements that are not fully covered by Django's default username-based authentication system.

The custom user model acts as the authentication entity while allowing future expansion of roles, permissions, and merchant workflows.

---

# Design Decisions

## Why Custom User Model?

Django's default User model uses a username-based authentication approach.

The platform requires:

- Email-based authentication
- Merchant-oriented accounts
- Flexible user roles
- Future permission expansion

Therefore, a custom user model was introduced from the beginning.

---

# Primary Key Design

The User model uses UUID as the primary key.

Benefits include:

- Non-sequential identifiers
- Better security when exposing identifiers externally
- Easier compatibility with distributed systems
- Reduced information leakage compared to incremental IDs

Example:

Instead of:

```text
/users/15/
```

The system uses UUID-based identifiers.

---

# Authentication Strategy

Authentication is based on email instead of username.

The email field represents the user's primary identity within the platform.

This approach better matches merchant systems where email is commonly used as the account identifier.

---

# Custom User Manager

User creation is handled through a dedicated custom manager.

The `CustomUserManager` centralizes user creation logic and enforces consistent business rules.

Responsibilities include:

- Creating regular users
- Creating superusers
- Handling email normalization
- Managing authentication-related defaults

Using a custom manager prevents user creation logic from being duplicated across different parts of the application.

---

# Store Relationship

Users can be associated with a Store.

The relationship represents the merchant ownership structure:

```text id="p4z0bd"
User

 |

 ▼

Store
```

Store owners and internal team members operate within the context of their assigned store.

---

# Superuser Exception

System administrators are not required to belong to a Store.

This separation allows platform-level administration without mixing system users with merchant tenant data.

Example:

```text id="9r6lzk"
Platform Admin

(no Store)

        |

        ▼

Manage Platform
```

---

# User Roles

The user model supports role-based classification.

Current roles include:

## Owner

Represents the merchant owner.

Responsibilities include:

- Managing store settings
- Managing team members
- Managing business resources

---

## Manager

Represents an internal employee created by the store owner.

Responsibilities include:

- Managing products
- Supporting daily operations

---

## Shipper

Represents operational delivery staff.

Future responsibilities may include:

- Handling deliveries
- Updating shipment status

---

# Forms and Validation

User operations are handled through dedicated Django Forms.

Forms provide:

- Input validation
- Business rule enforcement
- Consistent user creation and update workflows

Examples include:

- Merchant signup form
- User profile update form
- Staff creation forms

---

# Administration

The custom user model uses a customized Django Admin interface.

The admin configuration adapts Django's built-in `UserAdmin` functionality to support:

- Email-based authentication
- Custom fields
- Custom forms
- Role management

This preserves Django's built-in authentication administration features while supporting the custom model.

---

# Design Benefits

The custom user architecture provides:

- Flexible authentication design
- Clear separation between platform users and merchant users
- Future role expansion
- Better alignment with SaaS requirements
- Maintainable user management

---

# Future Evolution

Possible future improvements include:

- More granular permissions
- Django Groups integration
- Audit tracking
- User activity history
- Advanced role management

---

# Related Documentation

- `Database/base-models.md`
- `Database/store-model.md`
- `Database/tenant-isolation.md`
- `Architecture/authorization.md`
- `Architecture/user-management.md`
