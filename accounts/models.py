import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Manager for CustomUser where email is the unique identifier and
    store assignment is enforced for all non-superuser accounts.
    """

    def _create_user(self, email, password=None, **extra_fields):
        """
        Core user creation routine.
        Validates email, normalizes it, and ensures store is set for non-superusers.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email).lower()

        # Determine if this is a superuser (system-level, no store required)
        is_superuser = extra_fields.get("is_superuser", False)
        store = extra_fields.get("store")

        # For non-superusers, store is mandatory
        if not is_superuser and store is None:
            raise ValueError(_("Store must be assigned for non-superuser accounts."))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()  # triggers model validation
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create a regular user (must belong to a store).
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        # Store must be provided explicitly, otherwise raise error
        store = extra_fields.get("store")
        if store is None:
            raise ValueError(_("The store field is required for regular users."))

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a superuser (no store required; has all permissions).
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault(
            "role", CustomUser.Role.OWNER
        )  # default role for superusers

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        # Superuser should not have a store (or can be null)
        extra_fields["store"] = None

        return self._create_user(email, password, **extra_fields)
