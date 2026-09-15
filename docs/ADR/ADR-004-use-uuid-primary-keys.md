# ADR-004: Use UUID as Primary Keys

## Status

Accepted

---

## Context

The platform exposes and manages business resources in a SaaS environment.

Using predictable auto-increment integer identifiers can reveal resource ordering and make external references easier to guess.

The application also requires identifiers that work well with distributed systems and future integrations.

---

## Decision

Use UUID as the default primary key strategy for core application models.

UUID identifiers are used for entities where stable external references and non-sequential identifiers are beneficial.

Current examples include:

* Custom User
* Store
* Product
* Category
* ProductImage

---

## Benefits

* Prevents predictable sequential identifiers.
* Reduces the risk of simple identifier enumeration.
* Provides globally unique identifiers.
* Better suited for distributed systems.
* Simplifies future service integrations.
* Avoids exposing internal record counts or creation order.

---

## Trade-offs

* Larger database indexes compared to integer IDs.
* Slightly increased storage requirements.
* Potentially lower database performance in some scenarios.
* Less human-readable identifiers.

---

## Alternatives Considered

### Auto-increment Integer IDs

Rejected as the default strategy because sequential identifiers are easier to predict when exposed externally.

They may still be suitable for internal-only data where external exposure is not required.

---

## Security Note

UUID improves identifier unpredictability but does not replace proper security mechanisms.

Authentication and authorization remain required to prevent unauthorized access.

A user who has a valid UUID should still only access resources they are authorized to access.

---

## Related Documentation

* `Database/custom-user-model.md`
* `Database/store-model.md`
* `Database/product-model.md`
* `Decisions/design-principles.md`
