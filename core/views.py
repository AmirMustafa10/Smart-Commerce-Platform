from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

CustomUser = get_user_model()


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:dashboard")

        return super().get(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        user = self.request.user
        if user.role in (CustomUser.Role.OWNER, CustomUser.Role.MANAGER):
            template_name = "core/manager_dashboard.html"
        else:
            template_name = "core/shipper_dashboard.html"
        return template_name
