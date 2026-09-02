# Tenant Data Isolation

The application follows a strict tenant isolation strategy.

Business entities cannot reference data belonging to another store.

Current rules include:

- Product → Category must belong to the same Store.
- Staff → Store
- User → Store

This approach prevents cross-tenant data leakage and preserves data consistency.