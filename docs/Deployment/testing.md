# Testing Strategy

## Overview

The project uses Django's testing framework to verify application behavior and maintain code quality.

## Test Organization

Tests are organized by application layer:

### Models

Responsible for testing:

- Model behavior
- Data validation
- Relationships
- Constraints

### Forms

Responsible for testing:

- Form validation
- Input cleaning
- Business rules validation

### Views

Responsible for testing:

- HTTP responses
- Authentication behavior
- Template rendering
- Redirect logic

# Current Test Coverage

The project follows a layered testing strategy across implemented applications.

Current coverage includes:

## Accounts

- Models
- Forms
- Views

## Stores

- Models
- Forms
- Views

Tests verify:

- Business rules
- Validation
- Authentication
- Authorization
- View behavior
- Redirect logic
- Form processing
- Model integrity