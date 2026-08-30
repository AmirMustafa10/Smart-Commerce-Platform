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
