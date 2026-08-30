# ADR-002: Introduce TenantAwareModel

## Status

Accepted

## Context

The application is designed as a multi-tenant SaaS platform where business entities belong to a specific store.

Many models require the same relationship to a store.

## Decision

Introduce an abstract base model named `TenantAwareModel` that provides a shared relationship to the owning store.

Business models inherit from this base model instead of defining the relationship repeatedly.

## Benefits

- Eliminates duplicated code.
- Standardizes store ownership.
- Simplifies future maintenance.
- Provides a consistent foundation for tenant isolation.

## Alternatives

### Defining `store` in every model

Rejected because it duplicates code and increases maintenance effort.

## Consequences

Tenant isolation logic can later be implemented consistently using Managers, QuerySets, middleware, permissions, or service-layer filtering while relying on the shared store relationship.