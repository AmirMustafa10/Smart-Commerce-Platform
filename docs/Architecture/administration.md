# Administration

## Purpose

This document describes the administration strategy used in the Smart Commerce Platform.

It explains how Django Admin is customized to support platform management while preserving Django's built-in administrative capabilities.

---

## Scope

This document covers:

* Custom Django Admin configuration
* User administration
* Store administration
* Product administration
* Inline management

This document does **not** cover:

* Merchant dashboard functionality
* User authorization rules
* Business workflows
* Frontend interfaces

---

# Overview

The platform uses Django Admin as an internal management interface for managing system entities.

Instead of relying on Django's default administration configuration, the project customizes the admin interface to support the custom domain models and business requirements.

This approach allows efficient internal management while keeping the merchant-facing dashboard separate from administrative operations.

---

# Custom User Administration

The default Django User Admin is replaced with a customized administration interface.

The default configuration depends on Django's username-based authentication model, while the platform uses a custom user model with email-based authentication.

The custom admin extends Django's built-in `UserAdmin` functionality while adapting it to the project's requirements.

---

## Custom User Admin Capabilities

Current customization includes:

* Custom user display fields
* Custom add user form configuration
* Custom change user form configuration
* Search functionality
* Filtering options

Extending Django's existing `UserAdmin` preserves built-in authentication and permission management features while supporting the custom user model.

---

# Store Administration

The Store Admin provides an organized interface for managing tenant business entities.

Current responsibilities include:

* Managing store information
* Reviewing store configuration
* Managing store status

The admin interface supports internal platform management without exposing platform-level operations to merchant users.

---

# Product Administration

The Product Admin provides management capabilities for the product domain.

Current functionality includes:

* Product management
* Category relationship management
* Product information display
* Product image handling

---

# Product Image Inline Management

Product images are managed through an inline interface inside the Product Admin.

This approach allows administrators to manage related product images directly while editing the parent product.

Benefits include:

* Better administration experience
* Reduced navigation between pages
* Clear relationship visualization
* Easier content management

---

# Design Decisions

## Why Extend Built-in Admin Classes?

The project extends Django's existing admin classes instead of creating administration interfaces from scratch.

Benefits:

* Preserves Django's security features
* Avoids duplicating existing functionality
* Reduces maintenance cost
* Keeps compatibility with Django updates

---

## Why Not Use ModelAdmin for User Management?

A custom `ModelAdmin` implementation was considered.

However, it would require manually rebuilding features already provided by Django's `UserAdmin`, including:

* Permission management
* Password handling
* User-related workflows

Therefore, extending `UserAdmin` provides a cleaner and safer approach.

---

# Administration Principles

The administration layer follows these principles:

* Reuse framework capabilities
* Avoid unnecessary duplication
* Keep internal administration separate from user-facing features
* Provide efficient management workflows

---

# Future Evolution

Future improvements may include:

* Audit logging
* Admin activity tracking
* Advanced filtering
* Platform statistics dashboard
* Tenant management tools
* Administrative reports

---

# Related Documentation

* `Architecture/user-management.md`
* `Architecture/product-management.md`
* `Architecture/store-management.md`
* `Architecture/authorization.md`
* `ADR/ADR-004-custom-user-admin.md`
