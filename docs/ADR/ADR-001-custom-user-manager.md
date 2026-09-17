# ADR-001: Use a Custom User Manager

## Status

Accepted

---

## Context

The platform uses a custom authentication model with business-specific rules.

User creation is not only a technical operation but also requires enforcing application-level rules.

Merchant users must belong to a store, while platform administrators must be able to exist without a store assignment.

The system also supports different user roles and multiple account creation flows, such as:

* Merchant registration
* Staff account creation
* Administrative users

A centralized approach is required to ensure that all user creation processes follow the same rules.

---

## Decision

A custom `User Manager` is responsible for creating users and enforcing business rules during object creation.

All user creation flows should use the custom manager to maintain consistent behavior.

The manager:

* Validates required fields.
* Prevents creating merchant users without a store.
* Allows creating platform superusers without assigning a store.
* Handles user creation logic in one centralized location.
* Uses `using=self._db` to remain compatible with Django's multi-database support.

---

## Alternatives Considered

### Validation Only in Views

Rejected because validation becomes duplicated across different views and can be bypassed by other creation methods.

### Validation Only in Serializers

Rejected because it only protects REST API endpoints and does not cover other user creation flows.

### Database Constraints Only

Rejected because database constraints cannot provide clear application-level validation messages and may create poor developer experience.

---

## Consequences

### Advantages

* Centralized user creation logic.
* Consistent enforcement of business rules.
* Fail-fast validation.
* Easier maintenance.
* Compatible with future multi-database support.

### Disadvantages

* Slightly more code compared to Django's default user manager.
* Developers must use the custom manager instead of directly creating users.

---

## Related Documentation

* `Database/custom-user-model.md`
* `Database/tenant-isolation.md`
* `Architecture/user-management.md`
