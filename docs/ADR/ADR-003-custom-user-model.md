# ADR-003: Use a Custom User Model

## Status

Accepted

---

## Context

The platform requires an authentication system that supports merchant-specific business requirements.

Django's default User model provides a general authentication solution, but it is based on username-oriented authentication and does not directly support the platform's business needs.

The application requires:

* Email-based authentication.
* Merchant-specific user information.
* Store-related user relationships.
* Future role and permission expansion.

Introducing these requirements after the project grows would make migration more complex and expensive.

---

## Decision

Use a custom User model as the project's authentication model from the beginning.

The custom User model provides a flexible foundation for authentication and user management.

Current design decisions include:

* UUID as the primary key.
* Email as the authentication identifier.
* Support for merchant-related user data.
* Support for future role-based access control.
* Integration with a custom User Manager.
* Custom Django Admin integration.

---

## Alternatives Considered

### Django Default User Model

Rejected because it does not provide the required flexibility for merchant-specific fields and email-based authentication.

---

### Django Default User + Profile Model

Rejected because important user-related business information would be split across multiple models.

This increases complexity when implementing authentication rules, permissions, and user management workflows.

---

## Consequences

### Advantages

* Supports business-specific user requirements.
* Provides flexibility for future authentication changes.
* Enables role and permission expansion.
* Avoids costly user model migration in the future.
* Creates a clean foundation for SaaS user management.

### Disadvantages

* Requires maintaining custom forms and admin configuration.
* Developers must keep compatibility with Django authentication conventions.
* Adds more initial implementation effort compared to the default User model.

---

## Related Documentation

* `Database/custom-user-model.md`
* `ADR/ADR-001-custom-user-manager.md`
* `Architecture/user-management.md`
* `Architecture/authorization.md`
