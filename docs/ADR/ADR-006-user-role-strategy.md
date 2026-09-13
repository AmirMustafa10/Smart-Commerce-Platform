# ADR-004: Use Role-Based User Classification

## Status

Accepted

---

## Context

The application requires different types of users within the same store.

Initially, only store owners and shippers existed. As the application evolved, a manager role became necessary to delegate operational tasks such as product management.

A strategy was required to represent user roles.

---

## Decision

User roles are represented using a dedicated `role` field on the custom user model.

Current roles include:

- Owner
- Manager
- Shipper

Authorization logic is based on the assigned role.

---

## Alternatives Considered

### Django Groups

#### Advantages

- Built into Django.
- Flexible permission assignment.

#### Disadvantages

- Adds unnecessary complexity for the current project.
- Requires managing groups and permissions even though the role set is fixed.

**Decision:** Rejected for the current stage.

---

### Custom RBAC System

#### Advantages

- Highly flexible.
- Supports custom permissions.

#### Disadvantages

- Significant implementation complexity.
- Not required for the current business requirements.

**Decision:** Deferred.

---

### Role Field on Custom User

#### Advantages

- Simple implementation.
- Easy authorization checks.
- Fits the current business requirements.
- Easy to extend with additional roles later.

#### Disadvantages

- Less flexible than a full RBAC system.

**Decision:** Accepted.

---

## Consequences

### Positive

- Clear separation of user responsibilities.
- Simple authorization rules.
- Easier onboarding of additional predefined roles.

### Negative

- Future migration may be required if fully customizable permissions become necessary.