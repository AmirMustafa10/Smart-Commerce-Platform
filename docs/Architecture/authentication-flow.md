# Merchant Registration Flow

## Overview

The platform uses a dedicated `MerchantSignUpForm` to handle merchant registration.

Unlike normal user creation, merchant registration is a business workflow that creates multiple related entities.

## Flow

1. Validate merchant input.
2. Create the merchant user account.
3. Create the associated store.
4. Establish the relationship between the merchant and the store.

## Why Use a Form Instead of ModelForm?

A regular ModelForm is designed for handling a single model instance.

Merchant registration involves multiple models and business rules, therefore a standard Django Form provides better control over the workflow.

## Future Improvement

As the business logic grows, the registration process can be moved into a dedicated service layer.