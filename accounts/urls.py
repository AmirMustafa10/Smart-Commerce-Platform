from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.MerchantSignUpView.as_view(), name="signup"),
    path("login/", views.MerchantLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("team/", views.TeamListView.as_view(), name="team_list"),
    path("shippers/add/", views.ShipperCreateView.as_view(), name="shipper_create"),
    path(
        "shippers/<uuid:pk>/toggle/",
        views.ShipperToggleStatusView.as_view(),
        name="shipper_toggle",
    ),
    path(
        "team/<uuid:pk>/",
        views.MemberProfileView.as_view(),
        name="member_profile",
    ),
    path("profile/", views.MemberProfileView.as_view(), name="my_profile"),
    path("profile/edit/", views.UserProfileUpdateView.as_view(), name="profile_edit"),
    path(
        "profile/password/",
        views.CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
]
