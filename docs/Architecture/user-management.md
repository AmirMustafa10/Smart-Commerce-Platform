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

## Staff Account Management

Store owners can create and manage staff accounts through a dedicated creation form.

Currently, the system supports shipper accounts.

Store owners are responsible for:

- Creating shipper accounts
- Activating accounts
- Deactivating accounts

This approach keeps staff management under the control of the tenant while preserving account history.

Account activation is preferred over deletion to preserve historical data and maintain referential integrity across the system.

## Role-Based Dashboard

The application provides role-specific workspaces.

Currently:

- Store owners have access to the owner dashboard.
- Staff and administrative dashboards will be introduced separately.

This separation keeps each interface focused on the responsibilities of its corresponding role.

## Team Management

Team management functionality is available only to store owners.

This includes viewing and managing staff accounts while preventing access from non-owner users.

## Profile Management

Authenticated users can manage their personal account information through dedicated profile views.

Current functionality includes:

- View profile information
- Update profile details
- Change account password

Password updates are implemented by extending Django's built-in password change view, allowing customization while preserving Django's secure authentication workflow.
