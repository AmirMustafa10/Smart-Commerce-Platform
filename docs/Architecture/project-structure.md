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