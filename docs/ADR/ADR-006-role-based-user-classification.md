# ADR-006: Use Role-Based User Classification

## Status

Accepted

---

## Context

The platform allows multiple users to operate within the same merchant store.

Different users have different responsibilities and access levels.

Initially, the system supported store owners and shippers. As the platform evolved, a manager role became necessary to delegate operational responsibilities such as product management.

A decision was required to determine how user responsibilities should be represented and controlled.

---

## Decision

User roles are represented using a dedicated `role` field on the custom User model.

Current roles include:

- Owner
- Manager
- Shipper

Authorization decisions are based on the assigned role.

The role field represents the user's responsibility type, while future permission systems may provide more granular access control when required.

Current role responsibilities include:

| Role    | Responsibility                                       |
| ------- | ---------------------------------------------------- |
| Owner   | Manages store settings and team members              |
| Manager | Handles operational tasks such as product management |
| Shipper | Performs assigned shipping-related tasks             |

---

## Alternatives Considered

### Django Groups

#### Advantages

- Built into Django.
- Supports flexible permission assignment.

#### Disadvantages

- Adds additional complexity for the current fixed role requirements.
- Requires managing groups and permissions when only a small predefined role set exists.

**Decision:** Rejected for the current stage.

---

### Custom RBAC System

#### Advantages

- Highly flexible.
- Supports custom permissions and complex authorization rules.

#### Disadvantages

- Requires significant implementation effort.
- Not required for current business requirements.

**Decision:** Deferred.

---

### Permission Flags on User Model

Example:

```python
can_manage_products = models.BooleanField()
```

#### Advantages

- Simple for individual permissions.

#### Disadvantages

- Creates many fields as the system grows.
- Becomes difficult to maintain.
- Mixes user identity with permission configuration.

**Decision:** Rejected.

---

### Role Field on Custom User

#### Advantages

- Simple implementation.
- Clear user classification.
- Easy authorization checks.
- Fits current business requirements.
- Can be extended in the future.

#### Disadvantages

- Less flexible than a complete RBAC system.

**Decision:** Accepted.

---

## Consequences

### Positive

- Clear separation of user responsibilities.
- Simple authorization logic.
- Easier onboarding of predefined roles.
- Matches the current SaaS business model.

### Negative

- Custom permissions per user may require future architectural changes.
- A migration to a more flexible RBAC system may be required if permission complexity increases.

---

## Future Considerations

The current role-based approach can evolve into a more advanced permission system when required.

Possible future improvements:

- Custom permissions
- Store-level permission management
- Permission groups
- Audit logs for role changes

---

## Related Documentation

- `Database/custom-user-model.md`
- `Architecture/user-management.md`
- `Architecture/authorization.md`
- `ADR-003-custom-user-model.md`
