# Merchant Registration Flow

## Overview

The platform uses a dedicated `MerchantSignUpForm` to handle merchant registration.

Unlike normal user creation, merchant registration is a business workflow that creates multiple related entities.

## Authentication Flow

After successful merchant registration, the user is redirected to the dashboard.

Authentication entry points:

- `/accounts/signup/` → Merchant registration
- `/accounts/login/` → User login
- `/accounts/logout/` → User logout

Authenticated users access the application workspace through:

- `/dashboard/`

The landing page remains available as the public entry point.

Staff accounts are created internally by store owners and do not register through the public merchant registration process.

## Why Use a Form Instead of ModelForm?

A regular ModelForm is designed for handling a single model instance.

Merchant registration involves multiple models and business rules, therefore a standard Django Form provides better control over the workflow.

## Future Improvement

As the business logic grows, the registration process can be moved into a dedicated service layer.


## Authentication Views

Authentication is implemented using Django Class-Based Views (CBVs).

Current authentication endpoints include:

- Merchant registration
- User login
- User logout

### Why Class-Based Views?

CBVs provide a reusable and extensible architecture by supporting inheritance, mixins, and separation of responsibilities.

This approach aligns with Django's recommended practices for authentication workflows.

## Authentication Templates

Authentication pages are implemented using custom HTML templates styled with Bootstrap 5.

Django Crispy Forms is used where needed to simplify form rendering, while custom HTML is maintained to provide full control over the user interface and layout.

This approach balances development efficiency with UI flexibility.

Current templates:

- Merchant registration
- User login
