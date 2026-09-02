from django.urls import path

from . import views

app_name = "stores"

urlpatterns = [
    path("settings/", views.StoreSettingsView.as_view(), name="settings"),
    path("deactivate/", views.StoreDeactivateView.as_view(), name="deactivate"),
    path("activateView/", views.StoreActivateView.as_view(), name="activate"),
]
