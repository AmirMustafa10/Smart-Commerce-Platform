# Authentication Flow

## Purpose

This document describes the authentication workflow of the Smart Commerce Platform.

It explains how users enter the platform, authenticate, and access protected resources while keeping authentication independent from authorization and business logic.

---

## Scope

This document covers:

* Merchant registration
* User login
* User logout
* Dashboard access
* Internal user creation workflow

This document does **not** cover:

* User roles and permissions
* Database models
* Form implementation
* Authentication backend implementation

---

## Overview

The platform provides a dedicated authentication workflow designed for merchant-based businesses.

Unlike traditional applications where users simply create an account, merchant registration represents a business onboarding process that prepares the merchant to start using the platform immediately.

Once authenticated, users are redirected to the appropriate application entry point where they can access features according to their assigned permissions.

---

# Authentication Entry Points

The platform currently exposes the following authentication endpoints.

| Route         | Purpose                    |
| ------------- | -------------------------- |
| `/signup/`    | Merchant registration      |
| `/login/`     | User authentication        |
| `/logout/`    | User logout                |
| `/dashboard/` | Main application workspace |

The landing page remains publicly accessible without authentication.

---

# Merchant Registration Flow

Merchant registration is designed as a business onboarding process rather than a simple user creation form.

During registration, the platform creates the required business entities needed for the merchant to begin using the system.

After successful registration, the merchant is automatically redirected to the dashboard.

---

# Login Flow

Registered users authenticate using their credentials through the login page.

After successful authentication, users are redirected to the dashboard, which serves as the primary entry point to the application.

Unauthenticated users attempting to access protected resources are redirected to the login page.

---

# Logout Flow

Authenticated users can terminate their session at any time.

After logout, users are redirected to the public landing page, ensuring a clear separation between authenticated and public experiences.

---

# Internal User Management

Internal team members are **not** created through the public registration process.

Instead, store owners create staff accounts from within the application.

Current internal users include:

* Managers
* Shippers

This approach ensures that only verified merchants can manage internal team members.

---

# Authentication Principles

The authentication workflow follows these principles:

* Authentication is separated from authorization.
* Only merchants register through the public registration process.
* Internal users are managed exclusively by store owners.
* Public pages remain accessible without authentication.
* Protected resources always require authentication.

---

# Future Evolution

Future improvements may include:

* Email verification
* Password reset via email
* Two-factor authentication (2FA)
* Multi-factor authentication (MFA)
* Social authentication providers
* Device/session management

---

# Related Documentation

* `Architecture/application-routing.md`
* `Architecture/authorization.md`
* `Architecture/user-management.md`
* `Architecture/user-forms.md`
* `Development/testing.md`
* `ADR/ADR-001-custom-user-manager.md`
* `ADR/ADR-003-custom-user-model.md`
