# Product Management

## Overview

The `products` application manages the product catalog for each tenant.

## Product Categories

Categories are implemented as a dedicated model.

Each category belongs to a single store.

## Tenant Isolation

A product can only be associated with categories belonging to the same store.

This rule prevents cross-tenant relationships and preserves data integrity.

## Pricing

Products maintain multiple pricing values:

- Cost price
- Selling price
- Discount price

This separation supports reporting, profitability analysis, and promotional pricing.

## SKU

Each product includes a Stock Keeping Unit (SKU) to simplify inventory management and product identification.

## Product Images

Products support multiple images through a dedicated image model rather than storing images directly on the product.

This design improves scalability and keeps the product model lightweight.

## Image Validation

Uploaded images are validated using:

- File extension validation
- File size validation
- Pillow image verification

These validations help ensure that uploaded files are valid image assets before storage.

## Django Admin

The Product model is managed through a customized Django Admin interface.

Related product images are managed using Django Inline Models, allowing administrators to create and edit product images directly from the product administration page.

This improves usability and reduces the number of administrative actions required to maintain product data.
