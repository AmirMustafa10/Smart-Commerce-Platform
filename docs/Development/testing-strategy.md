# Testing Strategy

## Purpose

This document describes the testing strategy used in the Smart Commerce Platform.

The objective is to ensure that business rules, application behavior, and critical workflows remain reliable as the project evolves.

---

# Overview

Testing is organized by application and by responsibility.

Instead of placing all tests in a single file, each application separates tests according to the layer being tested.

This organization keeps the test suite maintainable and scalable.

---

# Current Test Structure

Each application contains its own test package.

Typical organization:

```text
tests/
├── test_models.py
├── test_forms.py
└── test_views.py
```

Each file focuses on one application layer.

---

# Model Testing

Model tests verify business rules and database behavior.

Examples include:

* Model creation

* Field validation

* Custom model methods

* Business constraints

* Relationship validation

* Soft deletion behavior

Models should reject invalid business states whenever possible.

---

# Form Testing

Form tests verify input validation before data reaches the database.

Typical responsibilities include:

* Required fields
* Validation rules
* Business validation
* Data cleaning
* Custom validation methods

Examples include:

* Merchant signup validation

* WhatsApp number validation

* Profile update validation

* Team member creation

* Order creation validation

---

# View Testing

View tests verify application workflows.

Examples include:

* Authentication requirements
* Authorization rules
* Successful requests
* Redirect behavior
* Template rendering
* Form submission

Views should coordinate application flow rather than contain complex business logic.

---

# Permission Testing

Permission tests verify that users can only access functionality appropriate to their role.

Examples include:

* Owner-only views

* Team management

* Store settings

* Dashboard access

* Product management

* Order access based on store ownership

Unauthorized users should receive the expected response or redirection.

---

# Business Rule Testing

Critical business rules should always be covered by automated tests.

Examples include:

* Product and Category must belong to the same Store.
* Tenant-owned resources remain isolated.
* Staff accounts are created correctly.
* Store activation and deactivation behave correctly.

---

# Order Workflow Testing

Order processing contains critical business rules that require automated testing.

Current scenarios include:

- Creating orders decreases product quantities.
- Removing order items restores product quantities.
- Cancelling orders restores product quantities.
- Restoring orders reapplies inventory changes.
- Soft-deleted orders remain available for historical analysis.
- Order items maintain valid product relationships.

These tests ensure that order lifecycle events do not create inconsistent inventory states.

---

# Test Organization Principles

The testing strategy follows these principles:

* Tests should remain isolated.
* Each test should verify one behavior.
* Business rules take priority over implementation details.
* Tests should be easy to read and maintain.

---

# Future Evolution

Future testing improvements may include:

* API tests

* Integration tests

* Performance testing

* Security testing

* End-to-end testing

* Load testing

* Automated signal testing

---

# Related Documentation

* `Architecture/authorization.md`
* `Architecture/store-management.md`
* `Architecture/product-management.md`
* `Decisions/design-principles.md`
