from django.db import models
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()


class OwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to restrict access to store owners only.
    """

    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated
            and user.store is not None
            and user.role == CustomUser.Role.OWNER
        )


class StoreManagerRequiredMixin(UserPassesTestMixin):
    """
    Restrict access to OWNER or MANAGER users that belong to a store.
    """

    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated
            and user.store_id is not None
            and user.role in ("OWNER", "MANAGER")
        )


class TenantQuerySetMixin:
    """
    Mixin to filter queryset based on the current user's store and exclude soft-deleted records.
    Must be used with LoginRequiredMixin to ensure user is authenticated.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(store=self.request.user.store)


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class TenantAwareModel(models.Model):
    """
    Abstract base model that enforces tenant isolation.
    All concrete business models (Product, Order, etc.) must inherit from this.
    """

    store = models.ForeignKey(
        "stores.Store",  # string reference to avoid circular imports
        on_delete=models.PROTECT,
        related_name="%(class)s_related",  # unique reverse accessor for each child model
        db_index=True,
        help_text=_("The store (tenant) this record belongs to."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    is_deleted = models.BooleanField(
        default=False,
        help_text="whether this %(class) is deleted. Unselect this instead of deleting.",
    )

    objects = ActiveManager()  # only not deleted
    all_objects = models.Manager()  # all include deleted

    class Meta:
        abstract = True

    def clean(self):
        """
        Ensure every tenant-aware model instance is always associated with a store.
        This is a critical security control to prevent accidental cross-tenant data leakage.
        """
        super().clean()
        if self.store_id is None:
            raise ValidationError({"store": _("A store (tenant) must be assigned.")})

    def save(self, *args, **kwargs):
        """Validate tenant association before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
