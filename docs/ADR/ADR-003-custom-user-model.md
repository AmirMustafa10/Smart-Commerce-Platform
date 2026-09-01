# ADR-003: Use a Custom User Model

## Status

Accepted

## Context

The platform requires merchant-specific user information and future extensibility beyond Django's default authentication model.

## Decision

Use a custom User model as the project's authentication model from the beginning.

## Benefits

- Supports merchant-specific fields.
- Simplifies future authentication changes.
- Easier extension for roles and permissions.
- Avoids costly migrations later.

## Alternatives

- Django default User model

## Consequences

The authentication system remains flexible and scalable for future business requirements.
