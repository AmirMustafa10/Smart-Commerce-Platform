# Project Structure

## Purpose

This document describes the high-level organization of the Smart Commerce Platform and explains the responsibility of each Django application.

The project follows a modular architecture where each application represents a distinct business domain. This approach improves maintainability, scalability, and separation of concerns while allowing the platform to evolve as new business domains are introduced.

---

## Scope

This document covers:

- Project organization
- Application responsibilities
- Shared architectural components
- Design principles

This document does **not** cover:

- Database schema
- Authentication workflow
- Authorization rules
- API implementation details
- Deployment configuration

---

## Overview

The Smart Commerce Platform is organized into independent Django applications.

Each application owns a specific business domain and is responsible for a well-defined set of functionality. This architecture minimizes coupling between applications, simplifies maintenance, and allows the platform to grow without requiring major structural changes.

As new business domains emerge, additional applications can be introduced while preserving the existing architecture.

---

# Applications

## Core

The `core` application contains project-wide functionality shared across the platform that does not belong to a specific business domain.

### Current Responsibilities

- Public landing page
- Dashboard entry point
- Shared templates
- Custom error pages
- Common views and shared functionality

The `core` application acts as the central layer that connects the platform without containing business-specific logic.

---

## Accounts

The `accounts` application manages user identity, authentication, and account-related operations.

### Current Responsibilities

- Custom User model
- Custom User Manager
- Merchant registration
- Internal staff account management
- User authentication
- User profile management
- Password management
- Authentication forms
- Custom Django Admin integration

Testing follows a layered strategy by separating model, form, and view tests, making the application easier to maintain as it grows.

---

## Stores

The `stores` application manages tenant-related business information.

Each merchant owns a single store, which acts as the root business entity for tenant-owned resources across the platform.

### Current Responsibilities

- Store model
- Tenant configuration
- Business information
- WhatsApp contact information
- Store settings
- Store activation
- Store deactivation

Testing follows the same layered testing strategy adopted throughout the project.

---

## Products

The `products` application manages each store's product catalog.

It is designed as an independent business domain responsible for organizing products while preserving tenant isolation.

### Current Responsibilities

- Product categories
- Products
- Product images
- Product pricing
- Inventory-related information
- Product validation
- Django Admin integration

Testing follows the same layered organization used across the project.

---

## Shared Components

Some architectural components are intentionally shared across multiple applications to encourage consistency and code reuse.

### Current Shared Components

- Tenant-aware base models
- Shared templates
- Common validation utilities
- Shared authentication infrastructure

These shared components reduce duplication while preserving clear architectural boundaries between business domains.

---

# Design Principles

The project structure follows several architectural principles:

- Separation of Concerns (SoC)
- Single Responsibility Principle (SRP)
- Domain-Oriented Organization
- High Cohesion
- Low Coupling
- Scalability
- Maintainability

Each Django application owns a specific business domain and should avoid containing functionality outside its primary responsibility.

---

# Future Evolution

The modular architecture allows new business domains to be introduced with minimal impact on the existing codebase.

Planned and potential future applications include:

- Orders
- WhatsApp Integration
- Webhooks
- Notifications
- Payments
- Analytics
- Public APIs
- Background Tasks

The architecture is intentionally designed to support long-term growth without significant refactoring.

---

# Related Documentation

- `Architecture/authentication-flow.md`
- `Architecture/application-routing.md`
- `Architecture/authorization.md`
- `Architecture/store-management.md`
- `Architecture/product-management.md`
- `Architecture/user-management.md`
- `Database/tenant-isolation.md`
