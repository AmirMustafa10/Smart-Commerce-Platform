# ADR-011: Use Django Signals for Order Business Rules

## Status

Accepted

---

## Context

The order lifecycle affects other business entities, especially product inventory.

When order events occur, the system must automatically update related data while keeping business logic organized and maintainable.

A design decision was required to determine where these automatic updates should be implemented.

The main goal was to keep order processing logic separated from inventory management while ensuring that data remains consistent.

---

## Decision

Use Django Signals to handle order-related business events.

Signals are responsible for triggering inventory updates when order-related changes occur.

Current behaviors include:

- Decreasing product quantity when order items are added.
- Restoring product quantity when order items are removed.
- Restoring product quantity when orders are cancelled.
- Reapplying quantity changes when orders are restored.
- Restoring affected quantities when orders are deleted.

This approach keeps inventory synchronization outside the model layer and allows different parts of the system to react automatically to business events.

---

## Alternatives Considered

## Implement Logic Directly in Views

Rejected because business rules would become duplicated across different application entry points.

This approach also makes future changes harder because inventory behavior would depend on specific views.

---

## Override Model Methods Only

Rejected because not all changes necessarily happen through the same model workflow.

Model methods may not cover all possible business events or future integrations.

---

## Service Layer Only

Deferred because the current application size does not require an additional abstraction layer.

A dedicated service layer can be introduced later when business workflows become more complex.

---

## Consequences

## Advantages

- Centralized business event handling.
- Reduced duplicated logic.
- Automatic synchronization between different domains.
- Better separation between data models and business workflows.
- Easier extension when new order events are introduced.

---

## Disadvantages

- Signals can become difficult to trace if overused.
- Complex workflows may require a dedicated service layer in the future.
- Debugging indirect execution flows may require additional documentation.

---

## Future Considerations

As business workflows become more complex, some signal logic may move into dedicated domain services while keeping event-based behavior.

Future improvements may include:

- Dedicated order services.
- Explicit domain event handling.
- More advanced workflow orchestration.