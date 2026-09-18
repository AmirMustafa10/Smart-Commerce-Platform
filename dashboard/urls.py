from django.urls import path
from .views import ManagerDashboardView, ShipperDashboardView

app_name = "dashboards"

urlpatterns = [
    path(
        "manager-dashboard/", ManagerDashboardView.as_view(), name="manager_dashboard"
    ),
    path("shipper-dashboard/", ShipperDashboardView.as_view(), name="shipper_dashboard"),
]
