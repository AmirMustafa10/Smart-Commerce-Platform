# User Forms Design

## Overview

The project uses Django's built-in `UserCreationForm` and `UserChangeForm` for managing the custom user model.

## Why Not a Regular ModelForm?

Although `ModelForm` can generate forms directly from models, it does not include user-specific security logic.

`UserCreationForm` extends Django's form functionality by providing:

- Password hashing through `set_password()`
- Password confirmation validation
- User-specific validation rules
- Secure password handling

`UserChangeForm` provides safe user updates by preventing direct password editing and integrating with Django's password management workflow.

## Comparison

| Feature | ModelForm | UserCreationForm/UserChangeForm |
|---|---|---|
| Model field generation | ✅ | ✅ |
| Password hashing | ❌ Manual | ✅ Built-in |
| Password confirmation | ❌ | ✅ |
| User-specific validation | ❌ | ✅ |
| Django Admin compatibility | Limited | ✅ |

## Decision

Use Django's specialized user forms instead of generic ModelForms to maintain security and follow Django authentication best practices.