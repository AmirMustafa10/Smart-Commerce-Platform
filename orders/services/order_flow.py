from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable
from django.core.exceptions import ValidationError
from django.db import transaction
from orders.models import Customer, Order, OrderItem
from products.models import Product
from products.services.query_planner import SearchFilters
from orders.services.order_resolution import resolve_product_for_order

EDIT_BLOCKED_STATUSES = {
    Order.Status.SHIPPED,
    Order.Status.DELIVERED,
    Order.Status.CANCELLED,
    Order.Status.RETURNED,
}


@dataclass(slots=True)
class PendingOrderDraftResult:
    order: Order | None
    clarification_needed: bool
    clarification_message: str = ""


def _validate_customer_product(customer: Customer, product: Product):
    """
    Make sure the product belongs to the same store as the customer
    and is currently available for sale.
    """

    if customer.store_id != product.store_id:
        raise ValidationError(
            "The selected product does not belong to " "the customer's store."
        )

    if not product.is_active:
        raise ValidationError(
            f"The product '{product.name}' " "is not available for sale."
        )


def _validate_quantity(quantity: int):
    """
    Make sure the Quantity must be greater than zero.
    """

    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")


def _validate_order_customer(order: Order, customer: Customer):
    """
    Make sure the order belongs to the current customer and store.
    """

    if order.store_id != customer.store_id:
        raise ValidationError("The order does not belong to " "the customer's store.")

    if order.customer_id != customer.id:
        raise ValidationError("The order does not belong to this customer.")

    if order.is_deleted:
        raise ValidationError("The order has already been deleted.")


def _validate_order_editable(order: Order):
    """
    Validate whether an order can currently be modified or deleted.
    """

    if order.status in EDIT_BLOCKED_STATUSES:
        raise ValidationError(
            (
                f"The order cannot be modified because its current "
                f"status is {order.get_status_display()}."
            )
        )


def _lock_order_for_customer(order: Order, customer: Customer) -> Order:
    """
    Locks the order row in the database to prevent multiple updates at the same time,
    and checks that the order belongs to the customer.
    """

    locked_order = (
        Order.objects.select_for_update()
        .select_related(
            "customer",
            "store",
        )
        .get(pk=order.pk)
    )

    _validate_order_customer(
        order=locked_order,
        customer=customer,
    )

    return locked_order


def _move_order_to_pending(
    order: Order,
):
    """
    Move a confirmed or preparing order back to PENDING.
    PENDING is required while the customer is changing an existing order.
    """

    if order.status != Order.Status.PENDING:
        order.status = Order.Status.PENDING

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )


def recalculate_order_total(order: Order) -> Decimal:
    """
    Recalculate the order total from its active OrderItems.
    """

    total = sum(
        # Uses a Generator Expression inside sum() to avoid creating an intermediate list in memory
        (item.subtotal for item in order.items.all() if not item.is_deleted),
        Decimal("0.00"),  # Initial total value for return Decimal without problems
    )

    if order.total_amount != total:
        order.total_amount = total

        order.save(
            update_fields=[
                "total_amount",
                "updated_at",
            ]
        )

    return total


@transaction.atomic
def create_pending_order(
    customer: Customer,
    product: Product,
    quantity: int = 1,
    notes: str = "",
    payment_method: str = Order.PaymentMethod.COD,
) -> Order:
    """
    Create a new WhatsApp AI order in PENDING status.

    PENDING means:
    The order exists but still requires customer confirmation.
    """

    _validate_customer_product(
        customer=customer,
        product=product,
    )

    _validate_quantity(quantity)

    order = Order.objects.create(
        store=customer.store,
        customer=customer,
        status=Order.Status.PENDING,
        source=Order.Source.WHATSAPP_AI,
        payment_method=payment_method,
        is_paid=False,
        total_amount=Decimal("0.00"),
        notes=notes,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        price_at_order=product.final_price,
    )

    recalculate_order_total(order)

    return order


@transaction.atomic
def add_item_to_pending_order(
    order: Order, product: Product, quantity: int = 1
) -> OrderItem:
    """
    Add a new product to an existing PENDING order.
    """

    if order.status != Order.Status.PENDING:
        raise ValidationError("Items can only be added to a pending order.")

    if order.is_deleted:
        raise ValidationError("Cannot modify a deleted order.")

    _validate_customer_product(
        customer=order.customer,
        product=product,
    )

    _validate_quantity(quantity)

    order_item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        price_at_order=product.final_price,
    )

    recalculate_order_total(order)

    return order_item


def set_pending_order_item_quantity(
    order: Order, product: Product, quantity: int
) -> OrderItem:
    """
    Set the quantity of a product inside a PENDING order.

    If the product does not already exist in the order,
    a new OrderItem is created.
    """

    if order.status != Order.Status.PENDING:
        raise ValidationError("Items can only be modified in a pending order.")

    if order.is_deleted:
        raise ValidationError("Cannot modify a deleted order.")

    _validate_customer_product(
        customer=order.customer,
        product=product,
    )

    _validate_quantity(quantity)

    existing_item = order.items.filter(
        product_id=product.id,
        is_deleted=False,
    ).first()

    if existing_item:
        existing_item.quantity = quantity

        existing_item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        recalculate_order_total(order)

        return existing_item

    return add_item_to_pending_order(
        order=order,
        product=product,
        quantity=quantity,
    )


@transaction.atomic
def begin_order_modification(order: Order, customer: Customer) -> Order:
    """
    Prepare an existing order for modification.

    If the order is CONFIRMED or PREPARING, it is moved back to PENDING.

    SHIPPED, DELIVERED, CANCELLED, and RETURNED orders cannot be modified.
    """

    locked_order = _lock_order_for_customer(
        order=order,
        customer=customer,
    )

    _validate_order_editable(locked_order)

    _move_order_to_pending(locked_order)

    return locked_order


@transaction.atomic
def add_item_to_existing_order(
    order: Order, customer: Customer, product: Product, quantity: int
) -> OrderItem:
    """
    Add a product to an existing editable order.

    CONFIRMED/PREPARING orders are first moved back to PENDING.
    """

    _validate_quantity(quantity)

    locked_order = _lock_order_for_customer(
        order=order,
        customer=customer,
    )

    _validate_order_editable(locked_order)

    _move_order_to_pending(locked_order)

    _validate_customer_product(
        customer=customer,
        product=product,
    )

    order_item = OrderItem.objects.create(
        order=locked_order,
        product=product,
        quantity=quantity,
        price_at_order=product.final_price,
    )

    recalculate_order_total(locked_order)

    return order_item


@transaction.atomic
def update_existing_order_item_quantity(
    order: Order, customer: Customer, product: Product, quantity: int
) -> OrderItem:
    """
    Update the quantity of an existing product in an editable order.

    The order becomes PENDING and must be confirmed again.
    """

    _validate_quantity(quantity)

    locked_order = _lock_order_for_customer(
        order=order,
        customer=customer,
    )

    _validate_order_editable(locked_order)

    _move_order_to_pending(locked_order)

    _validate_customer_product(
        customer=customer,
        product=product,
    )

    existing_item = locked_order.items.filter(
        product_id=product.id,
        is_deleted=False,
    ).first()

    if not existing_item:
        raise ValidationError(
            (f"The product '{product.name}' " "is not currently part of this order.")
        )

    existing_item.quantity = quantity

    existing_item.save(
        update_fields=[
            "quantity",
            "updated_at",
        ]
    )

    recalculate_order_total(locked_order)

    return existing_item


@transaction.atomic
def remove_item_from_existing_order(
    order: Order, customer: Customer, product: Product
) -> OrderItem:
    """
    Soft-delete a product from an editable order.

    The OrderItem itself is preserved for historical purposes.
    The order becomes PENDING and requires confirmation again.
    """

    locked_order = _lock_order_for_customer(
        order=order,
        customer=customer,
    )

    _validate_order_editable(locked_order)

    _move_order_to_pending(locked_order)

    existing_item = (
        locked_order.items.filter(
            product_id=product.id,
            is_deleted=False,
        )
        .select_for_update()
        .first()
    )

    if not existing_item:
        raise ValidationError(
            (f"The product '{product.name}' " "is not currently part of this order.")
        )

    active_items_count = locked_order.items.filter(is_deleted=False).count()

    if active_items_count == 1:
        raise ValidationError(
            (
                "The last product cannot be removed from the order. "
                "Delete the entire order instead."
            )
        )

    existing_item.is_deleted = True

    existing_item.save(
        update_fields=[
            "is_deleted",
            "updated_at",
        ]
    )

    recalculate_order_total(locked_order)

    return existing_item


@transaction.atomic
def soft_delete_order(order: Order, customer: Customer) -> Order:
    """
    Soft-delete an editable order.

    The database record remains preserved.
    """

    locked_order = _lock_order_for_customer(
        order=order,
        customer=customer,
    )

    _validate_order_editable(locked_order)

    locked_order.is_deleted = True

    locked_order.save(
        update_fields=[
            "is_deleted",
            "updated_at",
        ]
    )

    return locked_order


@transaction.atomic
def confirm_order(order: Order, customer: Customer) -> Order:
    """
    Confirm a PENDING order after customer confirmation.

    Allowed transition:

        PENDING → CONFIRMED
    """

    locked_order = (
        Order.objects.select_for_update()
        .select_related(
            "customer",
            "store",
        )
        .get(pk=order.pk)
    )

    if locked_order.store_id != customer.store_id:
        raise ValidationError("The order does not belong to the " "customer's store.")

    if locked_order.customer_id != customer.id:
        raise ValidationError("The order does not belong to this customer.")

    if locked_order.is_deleted:
        raise ValidationError("A deleted order cannot be confirmed.")

    if locked_order.status != Order.Status.PENDING:
        raise ValidationError(
            (
                "Only pending orders can be confirmed. "
                f"Current status: "
                f"{locked_order.get_status_display()}."
            )
        )

    if not locked_order.items.filter(is_deleted=False).exists():
        raise ValidationError("An order cannot be confirmed without products.")

    recalculate_order_total(locked_order)

    locked_order.status = Order.Status.CONFIRMED

    locked_order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return locked_order


def _build_item_filters(item_request) -> SearchFilters:
    """
    Convert an OrderItemRequest into SearchFilters.
    """

    return SearchFilters(
        min_price=getattr(
            item_request,
            "min_price",
            None,
        ),
        max_price=getattr(
            item_request,
            "max_price",
            None,
        ),
        category_id=getattr(
            item_request,
            "category_id",
            None,
        ),
    )


@transaction.atomic
def build_pending_order_draft(
    customer: Customer,
    order_items: Iterable[object],
    pending_order: Order | None = None,
) -> PendingOrderDraftResult:
    """
    Resolve all requested order items and create/update a PENDING
    order draft.

    Rules:

    1. Every item must have a quantity.
    2. Every item must resolve to exactly one product.
    3. If any item is ambiguous or missing information:
       - do not create/update the order.
    4. If a pending order already exists:
       - update existing products
       - add new products
    """

    resolved_quantities: dict = {}
    resolved_products: dict = {}

    clarification_messages: list[str] = []

    for index, item_request in enumerate(order_items, start=1):
        semantic_query = (
            getattr(
                item_request,
                "semantic_query",
                "",
            )
            or ""
        ).strip()

        quantity = getattr(
            item_request,
            "quantity",
            None,
        )

        if not semantic_query:
            clarification_messages.append(
                f"Item {index}: " "the product was not identified."
            )
            continue

        if quantity is None:
            clarification_messages.append(
                f"Item {index} " f"('{semantic_query}'): " "quantity is missing."
            )
            continue

        if quantity <= 0:
            clarification_messages.append(
                f"Item {index} "
                f"('{semantic_query}'): "
                "quantity must be greater than zero."
            )
            continue

        filters = _build_item_filters(item_request)

        resolution = resolve_product_for_order(
            customer=customer,
            semantic_query=semantic_query,
            filters=filters,
            limit=10,
        )

        if resolution.product:
            product = resolution.product

            resolved_products[product.id] = product

            resolved_quantities[product.id] = (
                resolved_quantities.get(
                    product.id,
                    0,
                )
                + quantity
            )

            continue

        if resolution.candidates:

            candidate_lines = []

            for (
                candidate_index,
                product,
            ) in enumerate(
                resolution.candidates,
                start=1,
            ):
                candidate_lines.append(
                    (
                        f"{candidate_index}. "
                        f"{product.name} | "
                        f"Price: "
                        f"{product.final_price}"
                    )
                )

            clarification_messages.append(
                "\n".join(
                    [
                        (
                            f"Item {index} "
                            f"('{semantic_query}') "
                            "matches multiple products:"
                        ),
                        *candidate_lines,
                        ("Ask the customer to choose " "the exact product."),
                    ]
                )
            )

            continue

        clarification_messages.append(
            f"Item {index} "
            f"('{semantic_query}'): "(
                resolution.reason or "No matching product was found."
            )
        )

    if clarification_messages:
        return PendingOrderDraftResult(
            order=None,
            clarification_needed=True,
            clarification_message="\n\n".join(clarification_messages),
        )

    if not resolved_products:
        return PendingOrderDraftResult(
            order=None,
            clarification_needed=True,
            clarification_message=("No valid order items were found."),
        )

    resolved_items = [
        (
            resolved_products[product_id],
            resolved_quantities[product_id],
        )
        for product_id in resolved_products
    ]

    # -----------------------------------------------------
    # Reuse an existing PENDING order.
    # -----------------------------------------------------

    if pending_order is not None:

        if pending_order.status != Order.Status.PENDING:
            raise ValidationError(
                ("Only pending orders can be used " "as order drafts.")
            )

        if pending_order.is_deleted:
            raise ValidationError("Cannot modify a deleted order.")

        if pending_order.store_id != customer.store_id:
            raise ValidationError(
                ("The pending order does not belong " "to the customer's store.")
            )

        if pending_order.customer_id != customer.id:
            raise ValidationError(
                ("The pending order does not belong " "to this customer.")
            )

        order = pending_order

        for product, quantity in resolved_items:

            set_pending_order_item_quantity(
                order=order,
                product=product,
                quantity=quantity,
            )

        recalculate_order_total(order)

        return PendingOrderDraftResult(
            order=order,
            clarification_needed=False,
            clarification_message="",
        )

    # -----------------------------------------------------
    # Create a new PENDING order.
    # -----------------------------------------------------

    first_product, first_quantity = resolved_items[0]

    order = create_pending_order(
        customer=customer,
        product=first_product,
        quantity=first_quantity,
    )

    for product, quantity in resolved_items[1:]:

        add_item_to_pending_order(
            order=order,
            product=product,
            quantity=quantity,
        )

    recalculate_order_total(order)

    return PendingOrderDraftResult(
        order=order,
        clarification_needed=False,
        clarification_message="",
    )
