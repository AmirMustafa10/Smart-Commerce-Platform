# Store Management

## Purpose

This document describes how stores are managed within the Smart Commerce Platform and explains the role of the Store as the root business entity for each tenant.

It outlines the responsibilities of the store domain, ownership rules, and management capabilities while keeping implementation details separate.

---

## Scope

This document covers:

- Store management
- Store ownership
- Store settings
- Store activation lifecycle
- Business information

This document does **not** cover:

- Authentication
- Authorization implementation
- Database schema
- Product management

---

## Overview

Each merchant owns a single store that represents their business within the platform.

The store serves as the root business entity for tenant-owned resources such as products, categories, team members, and future business modules.

This design establishes a clear ownership hierarchy while supporting complete tenant isolation.

---

# Store Responsibilities

The Store domain is responsible for managing business-level information.

Current responsibilities include:

- Business information
- WhatsApp contact information
- Store settings
- Store status
- Tenant configuration

As the platform evolves, additional business settings may be introduced without affecting other domains.

---

# Store Settings

Store owners can manage their business information through a dedicated settings interface.

Current configuration includes:

- Store information
- WhatsApp contact details

Future configuration options may include:

- Branding
- Business hours
- Notification preferences
- Subscription settings

---

# Store Lifecycle

Stores are never permanently removed during normal operation.

Instead, the platform supports activation and deactivation.

Deactivation temporarily disables business operations while preserving:

- Products
- Categories
- Team members
- Historical data
- Future business records

This approach maintains data integrity and prevents accidental data loss.

---

# Ownership Model

Each store has a single owner responsible for business administration.

The owner is responsible for:

- Managing store settings
- Creating internal staff accounts
- Activating or deactivating the store

Internal staff members operate within the store but do not own it.

---

# Design Principles

The Store domain follows these architectural principles:

- Single business owner per tenant
- Clear ownership hierarchy
- Tenant isolation
- Data preservation
- Separation of business configuration from authentication

The Store acts as the foundation for all tenant-owned business resources across the platform.

---

# Future Evolution

Future enhancements may include:

- Subscription management
- Billing information
- Business branding
- Multiple store locations
- Tax configuration
- Shipping settings
- Business operating hours

The current architecture allows these capabilities to be added without changing the ownership model.

---

# Related Documentation

- `Architecture/project-structure.md`
- `Architecture/application-routing.md`
- `Architecture/product-management.md`
- `Architecture/user-management.md`
- `Database/tenant-isolation.md`
  س
