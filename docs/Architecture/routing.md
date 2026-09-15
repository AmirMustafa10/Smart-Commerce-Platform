# Application Routing

## Purpose

This document describes the routing strategy used throughout the Smart Commerce Platform.

It explains how URLs are organized to separate public pages from authenticated business functionality while maintaining a scalable and maintainable routing structure.

---

## Scope

This document covers:

- Public routes
- Protected routes
- URL organization
- Routing strategy
- Application boundaries

This document does **not** cover:

- View implementations
- Authentication logic
- Authorization rules
- API routing
- Business logic

---

## Overview

The platform organizes URLs according to business domains rather than technical layers.

Each Django application owns its own URL configuration, allowing the routing structure to remain modular, scalable, and easy to maintain.

This organization reduces coupling between applications and simplifies future expansion.

---

# Public Routes

Public routes are accessible without authentication and introduce visitors to the platform.

### Current Public Routes

| Route      | Purpose               |
| ---------- | --------------------- |
| `/`        | Landing page          |
| `/signup/` | Merchant registration |
| `/login/`  | User authentication   |
| `/logout/` | User logout           |

Additional public pages may be introduced in the future, such as:

- About
- Pricing
- Contact
- Documentation
- Privacy Policy

---

# Protected Routes

Protected routes require authentication and provide access to tenant-specific business functionality.

### Current Route Groups

| Route Group    | Responsibility             |
| -------------- | -------------------------- |
| `/dashboard/`  | Main application workspace |
| `/categories/` | Category management        |
| `/products/`   | Product management         |
| `/team/`       | Internal team management   |
| `/profile/`    | User profile management    |
| `/settings/`   | Store configuration        |
| `/activate/`   | Store activation           |
| `/deactivate/` | Store deactivation         |

Each application is responsible for maintaining its own URL configuration while exposing a consistent interface through the project's root URL configuration.

---

# Routing Organization

The current routing structure is organized by business domain.

```text
Public
│
├── /
├── /signup/
├── /login/
└── /logout/

Authenticated
│
├── /dashboard/
├── /categories/
├── /products/
├── /team/
├── /profile/
├── /settings/
├── /activate/
└── /deactivate/
```

Each business domain owns its own routes, making the project easier to maintain and extend.

---

# Routing Principles

The routing strategy follows these architectural principles:

- Public and authenticated experiences are clearly separated.
- Each business domain manages its own URL configuration.
- URLs remain predictable and human-readable.
- Business functionality is never exposed through public routes.
- The routing structure supports future expansion with minimal refactoring.

---

# Future Evolution

As the platform grows, additional route groups may be introduced for new business domains, including:

- Orders
- WhatsApp Integration
- Notifications
- Analytics
- REST API endpoints
- Webhook endpoints

The modular routing strategy allows these additions without affecting existing applications.

---

# Related Documentation

- `Architecture/project-structure.md`
- `Architecture/authentication-flow.md`
- `Architecture/authorization.md`
- `Architecture/product-management.md`
- `Architecture/store-management.md`
