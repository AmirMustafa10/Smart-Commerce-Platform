# ADR-004: Use UUID as Primary Keys

## Status

Accepted

## Context

The platform exposes resources through APIs where predictable integer identifiers could facilitate resource enumeration.

## Decision

Use UUID as the primary key for business entities.

## Benefits

- Prevents predictable sequential identifiers.
- Reduces enumeration attacks.
- Better suited for distributed systems.
- Easier integration across services.

## Trade-offs

- Larger indexes.
- Slightly reduced database performance compared to integers.
- Less human-readable identifiers.

## Alternatives

- Auto-increment integer IDs

## Security Note

UUID improves identifier unpredictability but does not replace proper authentication and authorization.
