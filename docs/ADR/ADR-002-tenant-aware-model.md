# ADR-002: Introduce TenantAwareModel

## Status

Accepted

---

## Context

The platform is designed as a multi-tenant SaaS application where business data belongs to a specific merchant store.

The `Store` entity represents the tenant boundary.

Many business entities require the same ownership relationship with a store, such as:

* Products
* Categories
* Future business resources

Defining the store relationship repeatedly in every model would create duplicated code and increase the risk of inconsistent ownership implementation.

---

## Decision

Introduce an abstract base model named `TenantAwareModel`.

`TenantAwareModel` extends the shared `BaseModel` and provides a common relationship to the owning store.

Tenant-owned business models inherit from this base model instead of defining the store relationship independently.

The inheritance structure is:

```text
BaseModel
    |
    └── TenantAwareModel
              |
              ├── Product
              └── Category
```

The `Store` model itself does not inherit from `TenantAwareModel` because it represents the tenant boundary rather than belonging to another tenant.

---

## Alternatives Considered

### Defining `store` in Every Model

Rejected because it duplicates code and increases maintenance effort.

Each model would need to implement the same ownership relationship independently.

---

### Using User as the Ownership Reference

Rejected because users represent people accessing the business, not the business entity itself.

A store may contain multiple users with different roles, while ownership should remain connected to the merchant business.

---

### Implementing Tenant Ownership Only Through Views

Rejected because ownership rules should exist at the data model level and not depend only on specific application flows.

---

## Consequences

### Advantages

* Eliminates duplicated store relationship definitions.
* Standardizes tenant ownership across business models.
* Provides a consistent foundation for tenant isolation.
* Simplifies adding future tenant-aware resources.
* Keeps business ownership independent from individual users.

### Disadvantages

* Developers must understand which models should inherit from `TenantAwareModel`.
* Not every model can use this abstraction, especially root entities such as `Store`.

---

## Future Considerations

Tenant isolation logic can later be implemented consistently using:

* Custom Managers
* QuerySets
* Middleware
* Permissions
* Service-layer filtering

while relying on the shared store relationship.

---

## Related Documentation

* `Database/base-models.md`
* `Database/tenant-isolation.md`
* `Database/store-model.md`
* `Database/product-model.md`
