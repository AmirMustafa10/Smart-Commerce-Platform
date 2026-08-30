# ADR-001: Use a Custom User Manager

## Status

Accepted

## Context

The application uses a custom authentication model with business-specific rules.

Merchant users must always belong to a store, while platform administrators must not.

## Decision

A custom User Manager is responsible for creating users and validating business rules during object creation.

The manager:

- Validates required fields.
- Prevents creating merchant users without a store.
- Allows creating platform superusers without assigning a store.
- Uses `using=self._db` to remain compatible with Django's multi-database support.

## Alternatives Considered

### Validation only in Views

Rejected because validation becomes duplicated and easy to bypass.

### Validation only in Serializers

Rejected because it only protects REST API endpoints.

### Database Constraints only

Rejected because database errors provide poor developer and user experience.

## Consequences

### Advantages

- Centralized user creation.
- Fail-fast validation.
- Easier maintenance.
- Compatible with multiple databases.

### Disadvantages

- Slightly more code than the default manager.
