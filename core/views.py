from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

CustomUser = get_user_model()


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.role in (CustomUser.Role.OWNER, CustomUser.Role.MANAGER):
                return redirect("dashboards:manager_dashboard")
            else:
                return redirect("dashboards:shipper_dashboard")

        return super().get(request, *args, **kwargs)

