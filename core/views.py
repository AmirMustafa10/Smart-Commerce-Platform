from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):

    def get_template_names(self):

        if self.request.user.is_authenticated:
            return ["core/dashboard.html"]

        return ["core/home.html"]
