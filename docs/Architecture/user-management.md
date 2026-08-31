# User Management

## Custom User Admin

The project uses a customized Django Admin interface for the custom user model.

The default Django User Admin was replaced because it relies on the default username-based authentication model.

## Implementation

The custom admin extends Django's built-in `UserAdmin` functionality while adapting:

- Display fields
- Add user form configuration
- Change user form configuration
- Search and filtering options

## Benefits

- Maintains Django's built-in permission management.
- Supports custom authentication fields.
- Provides a better administration experience for merchants.

## Alternative Considered

### Building Admin from ModelAdmin

Rejected because it requires manually recreating existing Django authentication admin features.

## Store Administration

The project provides a customized Django Admin interface for managing tenant stores.

The Store Admin configuration improves management efficiency by providing a structured interface for store operations.

Future improvements may include:

- Store activity tracking
- Tenant-specific permissions
- Audit logging
- Store statistics
