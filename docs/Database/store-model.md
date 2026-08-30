# Store Model

## Purpose

The `Store` model represents a merchant's business within the platform.

Each merchant operates through a dedicated store, and all business entities such as products, customers, and orders belong to a store.

## Responsibilities

- Store identity
- Business information
- WhatsApp contact number
- Ownership reference for tenant-aware models

## Validation

The WhatsApp phone number is validated using a regular expression to ensure only valid numbers are stored.

## Relationships

The Store model acts as the parent entity for all tenant-owned resources through the `TenantAwareModel` abstraction.

Future related models include:

- Products
- Categories
- Customers
- Orders
- Inventory
