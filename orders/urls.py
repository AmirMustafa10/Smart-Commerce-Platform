from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # -----------------------------------------
    # Core Order URLs (Manager / Owner / Shipper)
    # -----------------------------------------
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path(
        "orders/<uuid:pk>/detail/",
        views.OrderDetailView.as_view(),
        name="order_detail",
    ),
    # -----------------------------------------
    # (Manager / Owner) Specific URLs
    # -----------------------------------------
    path("orders/create/", views.OrderCreateView.as_view(), name="order_create"),
    path(
        "orders/<uuid:pk>/edit/", views.OrderUpdateView.as_view(), name="order_update"
    ),
    path(
        "orders/<uuid:pk>/delete/",
        views.OrderSoftDeleteView.as_view(),
        name="order_delete",
    ),
    # -----------------------------------------
    # Shipper Specific URLs (Available & Take Order)
    # -----------------------------------------
    path(
        "orders/available/",
        views.AvailableOrdersListView.as_view(),
        name="available_orders",
    ),
    path("orders/<uuid:pk>/take/", views.TakeOrderView.as_view(), name="take_order"),
    path(
        "orders/<uuid:pk>/shipper-update/",
        views.ShipperOrderUpdateView.as_view(),
        name="shipper_order_update",
    ),
    path("settlements/", views.SettlementListView.as_view(), name="settlements"),
    path(
        "settlements/<uuid:shipper_id>/clear/",
        views.SettleCashView.as_view(),
        name="clear_settlement",
    ),
]
