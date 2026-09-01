# User Model

The application uses a custom User model as the authentication entity.

Key characteristics:

- UUID primary key
- Merchant-oriented authentication
- Managed through a custom User Manager
- Extensible for future roles and permissions

## Forms

The custom User model is managed through dedicated Django Forms to ensure consistent validation during creation and updates.
