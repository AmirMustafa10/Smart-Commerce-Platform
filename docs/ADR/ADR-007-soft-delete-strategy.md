# ADR-007: Implement Soft Delete Strategy

## Status

Accepted

---

## Context

The platform manages business data where permanent deletion may cause loss of important historical information.

In a SaaS environment, removing records permanently can affect relationships between entities and make future reporting, auditing, and data recovery difficult.

Examples of data that may require preservation include:

* Stores
* Users
* Products
* Product images
* Future orders and transactions

A deletion strategy was required that preserves data while preventing deleted records from appearing in normal application workflows.

---

## Decision

Implement a Soft Delete strategy using a shared model behavior.

The base model provides deletion tracking fields:

* `is_deleted`
* `deleted_at`

Records are not physically removed from the database.

Instead:

* Normal queries use the default manager to exclude deleted records.
* A dedicated manager provides access to all records when required.

Example:

```python
objects
```

Returns active records only.

```python
all_objects
```

Returns all records including deleted ones.

---

## Alternatives Considered

### Permanent Database Deletion

#### Advantages

* Simple implementation.
* Removes unused data permanently.

#### Disadvantages

* Permanent data loss.
* Breaks historical relationships.
* Prevents recovery.
* Makes auditing difficult.

**Decision:** Rejected.

---

### Database Archive Tables

#### Advantages

* Keeps deleted data separately.
* Allows historical storage.

#### Disadvantages

* Requires additional database management.
* Increases complexity.
* Requires moving records between tables.

**Decision:** Deferred.

---

### Soft Delete Strategy

#### Advantages

* Preserves historical data.
* Allows recovery.
* Maintains relationships.
* Supports future auditing.
* Prevents accidental permanent deletion.

#### Disadvantages

* Requires filtering deleted records.
* Database size continues growing.
* Developers must understand manager behavior.

**Decision:** Accepted.

---

## Consequences

### Positive

* Protects important business data.
* Maintains referential integrity.
* Supports future reporting and analytics.
* Allows recovery from accidental deletion.
* Provides safer data management.

### Negative

* Deleted records remain in the database.
* Queries require correct manager usage.
* Additional storage is required.

---

## Future Considerations

The soft delete system can be extended with:

* Restore functionality.
* Deletion audit logs.
* Automatic cleanup policies.
* Admin views for deleted records.
* Retention policies.

---

## Related Documentation

* `Database/base-models.md`
* `Database/tenant-isolation.md`
* `Decisions/design-principles.md`
