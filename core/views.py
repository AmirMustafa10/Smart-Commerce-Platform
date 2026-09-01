from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import OwnerRequiredMixin

CustomUser = get_user_model()


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == CustomUser.Role.OWNER:
            return redirect("core:dashboard") 

        return super().get(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, OwnerRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"
