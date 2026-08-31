# Project Structure

## Applications

### Accounts

The `accounts` application manages authentication and merchant identity across the platform.

Current responsibilities include:

- Custom User model
- Custom User Manager
- Merchant registration
- User authentication (login/logout)
- User management
- Authentication forms
- Custom Django Admin integration

The application is registered using its AppConfig:

```python
accounts.apps.AccountsConfig
```

Using AppConfig improves project extensibility and provides a centralized place for application initialization, such as registering Django signals through the `ready()` method when needed.
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