# ADR-008: Introduce Shared BaseModel

## Status

Accepted

---

## Context

The platform contains multiple database models that share common behaviors and fields.

Repeating the same fields across every model increases duplication and makes future changes harder to maintain.

The application requires a consistent foundation for common model functionality, including:

* Unique identification
* Creation tracking
* Update tracking
* Shared lifecycle behavior

A reusable abstraction was required to avoid repeating the same implementation across different models.

---

## Decision

Introduce an abstract `BaseModel` that provides common fields and behaviors shared across application models.

Models that require these shared features inherit from `BaseModel` instead of implementing them individually.

The base model provides:

* UUID primary key strategy.
* Creation timestamp.
* Update timestamp.
* Common lifecycle behavior.

The inheritance structure is:

```text
BaseModel

    |

    ├── Store
    ├── Product
    ├── Category
    └── ProductImage
```

The model is abstract and does not create its own database table.

---

## Alternatives Considered

### Repeating Common Fields in Every Model

Example:

```python
id = UUIDField(...)
created_at = DateTimeField(...)
updated_at = DateTimeField(...)
```

#### Advantages

* Simple implementation for small projects.

#### Disadvantages

* Duplicated code.
* Higher maintenance effort.
* Inconsistent changes across models.

**Decision:** Rejected.

---

### Using Django Built-in Models Without Abstraction

#### Advantages

* No additional abstraction layer.
* Simpler initial setup.

#### Disadvantages

* Does not solve shared business requirements.
* Requires repeated customization.

**Decision:** Rejected.

---

### Shared Abstract Base Model

#### Advantages

* Reduces duplicated code.
* Standardizes common behavior.
* Simplifies future changes.
* Provides a consistent model foundation.

#### Disadvantages

* Developers must understand inheritance structure.
* Requires deciding which models should use the abstraction.

**Decision:** Accepted.

---

## Consequences

### Positive

* Cleaner database model design.
* Consistent primary key strategy.
* Centralized common behavior.
* Easier maintenance.
* Faster development of future models.

### Negative

* Adds an abstraction layer.
* Incorrect usage may create unnecessary inheritance.

---

## Relationship With TenantAwareModel

`TenantAwareModel` builds on top of `BaseModel` by adding store ownership for tenant-specific resources.

The hierarchy becomes:

```text
BaseModel

    |

    └── TenantAwareModel

            |

            ├── Product
            └── Category
```

Not every model belongs to a tenant, therefore not every model should inherit from `TenantAwareModel`.

---

## Future Considerations

The base model can support additional shared behaviors when required, such as:

* Audit fields.
* Common validation helpers.
* Shared model utilities.

---

## Related Documentation

* `Database/base-models.md`
* `Database/tenant-isolation.md`
* `ADR-002-tenant-aware-model.md`
* `ADR-007-soft-delete-strategy.md`
