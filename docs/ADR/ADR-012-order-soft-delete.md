# ADR-012: Use Soft Delete for Orders

## Status

Accepted

---

## Context

Orders represent important business records that are required for reporting, analytics, and historical tracking.

Permanent deletion would remove valuable information needed for future business operations.

A strategy was required to preserve order history while allowing normal application workflows to hide removed records.

The main goal was to balance data preservation with operational flexibility.

---

## Decision

Use soft deletion for Order records.

Instead of permanently removing orders, the system marks them as deleted while preserving the original data.

Deleted orders remain available for:

- Historical analysis
- Dashboard statistics
- Internal recovery workflows
- Future reporting

This approach ensures that important business information is preserved while preventing deleted orders from appearing in normal workflows.

---

## Alternatives Considered

## Permanent Deletion

Rejected because removing orders would permanently lose important business history and negatively affect analytics accuracy.

---

## Archive Table

Deferred because the current application does not require moving deleted records into separate storage.

A separate archive strategy can be considered later if data volume or compliance requirements increase.

---

## Consequences

## Advantages

- Preserves business history.
- Maintains accurate reporting.
- Allows future recovery workflows.
- Prevents accidental permanent data loss.
- Supports future analytics and auditing requirements.

---

## Disadvantages

- Requires filtering deleted records from normal queries.
- Database storage continues growing over time.
- Additional logic is required when handling restored records.

---

## Implementation

The platform uses:

- `is_deleted` to indicate deletion state.
- `deleted_at` to record deletion time.
- Default managers to hide deleted records.
- `all_objects` manager for internal access.

This implementation keeps normal application workflows clean while allowing internal operations to access historical data when required.

---

## Future Considerations

Future improvements may include:

- Automatic data retention policies.
- Audit history tracking.
- Advanced restore workflows.
- Scheduled cleanup strategies for old records.