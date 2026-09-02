from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model

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
