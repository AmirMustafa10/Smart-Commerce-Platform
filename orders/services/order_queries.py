from uuid import UUID
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from orders.models import Customer, Order, OrderItem

DEFAULT_ORDERS_LIMIT = 20


def _order_items_queryset():
    """
    Common queryset for loading order items together with
    their product and product category.
    """

    return (
        OrderItem.objects.select_related(
            "product",
            "product__category",
        )
        .filter(
            is_deleted=False,
        )
        .order_by("id")
    )


def get_order_by_id(order_id: str | UUID, customer: Customer) -> Order:
    """
    Get a specific order belonging to the current customer
    and the current store.

    Used for:
    - order_status
    - order_details
    - order modification
    - order deletion
    """

    if not order_id:
        raise ValidationError("Order ID is required.")

    try:
        order_uuid = UUID(str(order_id))
    except (ValueError, TypeError):
        raise ValidationError("Invalid order ID.")

    order = (
        Order.objects.select_related(
            "customer",
            "store",
            "shipper",
        )
        .prefetch_related(
            Prefetch(
                "items",
                queryset=_order_items_queryset(),
            )
        )
        .filter(
            id__icontains=order_uuid,
            customer_id=customer.id,
            store_id=customer.store_id,
            is_deleted=False,
        )
        .first()
    )

    if not order:
        raise ValidationError("Order not found.")

    return order


def get_latest_pending_order(customer: Customer) -> Order | None:
    """
    Return the customer's latest active PENDING order.

    Used for:
    - order confirmation
    - current order details
    - pending order modification
    """

    return (
        Order.objects.select_related(
            "customer",
            "store",
            "shipper",
        )
        .prefetch_related(
            Prefetch(
                "items",
                queryset=_order_items_queryset(),
            )
        )
        .filter(
            customer_id=customer.id,
            store_id=customer.store_id,
            status=Order.Status.PENDING,
            is_deleted=False,
        )
        .order_by("-created_at")
        .first()
    )


def get_latest_customer_order(customer: Customer) -> Order | None:
    """
    Return the customer's latest active order for the current store.

    Used when the customer refers to their current/recent order
    without providing an Order UUID.
    """

    return (
        Order.objects.select_related(
            "customer",
            "store",
            "shipper",
        )
        .prefetch_related(
            Prefetch(
                "items",
                queryset=_order_items_queryset(),
            )
        )
        .filter(
            customer_id=customer.id,
            store_id=customer.store_id,
            is_deleted=False,
        )
        .order_by("-created_at")
        .first()
    )


def get_customer_orders(customer: Customer, limit: int = DEFAULT_ORDERS_LIMIT):
    """
    Return the customer's recent active orders for the current store.

    Used for:
    - order_list
    """

    if limit <= 0:
        raise ValidationError("Limit must be greater than zero.")

    return (
        Order.objects.select_related(
            "customer",
        )
        .filter(
            customer_id=customer.id,
            store_id=customer.store_id,
            is_deleted=False,
        )
        .order_by("-created_at")[:limit]
    )


def get_order_details(order_id: str | UUID, customer: Customer) -> Order:
    """
    Return a specific customer's order with all its
    non-deleted items and product details.

    Used for:
    - order_details
    """

    return get_order_by_id(
        order_id=order_id,
        customer=customer,
    )
