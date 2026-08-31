# Project Structure

## Applications

### Accounts

The `accounts` application is responsible for authentication and user-related functionality.

Current responsibilities include:

- User authentication
- Merchant accounts
- User management

The application is registered using its AppConfig:

```python
accounts.apps.AccountsConfig
```

Using AppConfig ensures better extensibility and allows future initialization logic such as Django signals through the `ready()` method.

### Stores

The `stores` application is responsible for managing merchant stores and store-related business data.

Its responsibilities will include:

- Store information
- Store settings
- Business configuration
- Future store-related features

The application is registered using:

```python
stores.apps.StoresConfig
```

This keeps business logic separated from authentication and improves maintainability.

## Authentication

The project uses a custom User Manager to centralize user creation and enforce business rules consistently across the application.

## Shared Models

The project introduces an abstract `TenantAwareModel` to centralize store ownership across business entities.

Models that belong to a merchant inherit from this base model to ensure consistency and reduce code duplication.

## Stores

The `stores` application manages merchant businesses.

Its main entity is the `Store` model, which represents a merchant's business and serves as the ownership root for tenant-aware resources.

Current responsibilities include:

- Business information
- WhatsApp contact details
- Store configuration

### Core

The `core` application contains project-wide pages and shared functionality that do not belong to a specific business domain.

Current responsibilities include:

- Landing page
- Dashboard entry point
- Shared templates
- Error pages
- Common views