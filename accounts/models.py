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


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model representing a user within the multi‑tenant system.
    A user can be a store owner or a shipper and is always linked to a Store,
    except for system-level superusers.
    """

    class Role(models.TextChoices):
        OWNER = "OWNER", _("Store Owner")
        SHIPPER = "SHIPPER", _("Shipper")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the user."),
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        db_index=True,
        help_text=_("Required. Used as the primary login identifier."),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    store = models.ForeignKey(
        "stores.Store",  # string reference to avoid circular imports
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        help_text=_(
            "The store (tenant) this user belongs to. Null only for superusers."
        ),
    )
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=Role.choices,
        help_text=_("Role of the user within the store."),
    )
    full_name = models.CharField(
        _("full name"),
        max_length=150,
        help_text=_("Required. The user's full name."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active."),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS in Terminal command
    REQUIRED_FIELDS = [
        "full_name",
        "role",
    ]  # store is conditional and handled in manager

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["store", "role"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name.strip()

    def get_short_name(self):
        """Return the first part of the full name or email."""
        return self.full_name.split()[0] if self.full_name else self.email

    def clean(self):
        """
        Perform custom validation:
        - Normalize email (lowercase, strip).
        - Strip whitespace from full_name.
        - Ensure store is set for all non-superusers.
        """
        super().clean()

        # Normalize email
        if self.email:
            self.email = self.email.strip().lower()

        # Normalize full_name
        if self.full_name:
            self.full_name = self.full_name.strip()
            if not self.full_name:
                raise ValidationError({"full_name": _("Full name cannot be blank.")})

        # Enforce store requirement: only superusers may have store=None
        if not self.is_superuser and self.store_id is None:
            raise ValidationError(
                {"store": _("A store must be assigned to non-superuser accounts.")}
            )

    def save(self, *args, **kwargs):
        """Validate before saving to ensure data integrity."""
        self.full_clean()
        super().save(*args, **kwargs)
