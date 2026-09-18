from django.urls import path
from .views import ManagerDashboardView, ShipperDashboardView

app_name = "dashboards"

urlpatterns = [
    path("dashboard/", ManagerDashboardView.as_view(), name="manager_dashboard"),
]
