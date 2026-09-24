import re
from types import SimpleNamespace
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from orders.models import Order
from orders.services.order_flow import (
    EDIT_BLOCKED_STATUSES,
    add_item_to_existing_order,
    build_pending_order_draft,
    confirm_order,
    remove_item_from_existing_order,
    soft_delete_order,
    update_existing_order_item_quantity,
)
from orders.services.order_queries import (
    get_customer_orders,
    get_latest_customer_order,
    get_latest_pending_order,
    get_order_by_id,
    get_order_details,
)
from orders.services.order_resolution import (
    resolve_product_for_order,
)
from products.services.query_planner import (
    SearchFilters,
)

CUSTOMER_ORDERS_LIMIT = 20

DELETE_CONFIRMATION_TTL_SECONDS = 300
DELETE_CONFIRMATION_PREFIX = "whatsflow:order-delete-confirmation"

CURRENT_ORDER_TTL_SECONDS = 600
CURRENT_ORDER_PREFIX = "whatsflow:current-order"


ORDER_UUID_PATTERN = re.compile(
    r"\b"
    r"[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}"
    r"\b"
)

ORDER_UUID_PREFIX_PATTERN = re.compile(
    r"\b"
    r"(?=[0-9a-fA-F]{8}\b)(?=[^|\n]*\d)"
    r"([0-9a-fA-F]{8}"
    r"(?:-[0-9a-fA-F]{4}"
    r"(?:-[0-9a-fA-F]{4}"
    r"(?:-[0-9a-fA-F]{4}"
    r"(?:-[0-9a-fA-F]{12})?)?)?)?)"
    r"\b"
)


def _extract_order_uuid(text: str) -> str | None:
    match = ORDER_UUID_PATTERN.search(text or "")
    if match:
        return match.group(0)
    return None


def _extract_order_uuid_prefix(text: str) -> str | None:
    """
    Extracts a short UUID prefix (for example, `f3a0ffef-ec88`) from the text to help find an order or identify the customer’s request.
    Returns `None` if no UUID prefix is found.
    """

    match = ORDER_UUID_PREFIX_PATTERN.search(text or "")
    if match:
        return match.group(1)
    return None


# Creates a cache key for a pending delete confirmation
def _delete_confirmation_key(conversation_id) -> str:
    return f"{DELETE_CONFIRMATION_PREFIX}:{conversation_id}"


# Creates a cache key for the current order.
def _current_order_key(conversation_id) -> str:
    return f"{CURRENT_ORDER_PREFIX}:{conversation_id}"


# Saves the order ID that is waiting for delete confirmation
def _set_pending_delete_confirmation(conversation_id, order_id):
    cache.set(
        _delete_confirmation_key(conversation_id),
        str(order_id),
        timeout=DELETE_CONFIRMATION_TTL_SECONDS,
    )


# Gets the order ID waiting for delete confirmation
def _get_pending_delete_confirmation(conversation_id):
    return cache.get(_delete_confirmation_key(conversation_id))


# Removes the pending delete confirmation
def _clear_pending_delete_confirmation(conversation_id):
    cache.delete(_delete_confirmation_key(conversation_id))


# Saves the current order ID in the cache.
def _set_current_order(conversation_id, order_id):
    cache.set(
        _current_order_key(conversation_id),
        str(order_id),
        timeout=CURRENT_ORDER_TTL_SECONDS,
    )


# Gets the current order ID from the cache
def _get_current_order(conversation_id):
    return cache.get(_current_order_key(conversation_id))


# Removes the current order from the cache
def _clear_current_order(conversation_id):
    cache.delete(_current_order_key(conversation_id))


def _normalize_confirmation_text(text: str) -> str:
    """
    Converts the user's confirmation response to lowercase, removes punctuation, and replaces multiple spaces with a single space to make keyword matching easier.
    """

    text = (text or "").strip().casefold()

    text = re.sub(r"[؟?!.,،؛:]+", " ", text)

    return " ".join(text.split())


def _parse_delete_confirmation(text: str) -> str:
    """
    Return one of:

    - confirm
    - cancel
    - unclear

    Explicit deletion phrases are treated as confirmation,
    while phrases such as "مش قصدي ده" are treated as cancellation.
    """

    normalized = _normalize_confirmation_text(text)

    if not normalized:
        return "unclear"

    negative_clarification_phrases = (
        "مش قصدي",
        "مش ده",
        "مش المقصود",
        "مش الطلب ده",
        "مش الاوردر ده",
        "مش الأوردر ده",
        "لا مش قصدي",
        "لأ مش قصدي",
        "no i did not mean",
        "not this order",
    )

    if any(phrase in normalized for phrase in negative_clarification_phrases):
        return "cancel"

    explicit_delete_phrases = (
        "احذفه",
        "احذفها",
        "احذف الاوردر",
        "احذف الأوردر",
        "الغيه",
        "ألغيه",
        "الغاء الطلب",
        "إلغاء الطلب",
        "delete it",
        "cancel it",
    )

    if any(phrase in normalized for phrase in explicit_delete_phrases):
        return "confirm"

    positive_phrases = (
        "ايوه",
        "أيوه",
        "اه",
        "أه",
        "yes",
        "نعم",
        "موافق",
        "تمام",
        "ماشي",
        "أكيد",
        "اكيد",
        "متأكد",
        "أنا متأكد",
        "i am sure",
        "confirm",
    )

    if any(phrase in normalized for phrase in positive_phrases):
        return "confirm"

    negative_phrases = (
        "لا",
        "لأ",
        "لاء",
        "no",
        "مش",
        "not now",
    )

    if normalized in negative_phrases:
        return "cancel"

    return "unclear"


def _get_target_order(customer, order_id=None):
    """
    Resolve the order the customer is referring to.

    Priority:
    1. Explicit Order UUID
    2. Latest PENDING order
    """

    if order_id:
        return get_order_by_id(
            order_id=order_id,
            customer=customer,
        )

    pending_order = get_latest_pending_order(customer)

    if not pending_order:
        raise ValidationError("No active order was found for the current customer.")

    return pending_order


def _get_delete_target_order(customer, order_id=None):
    """
    Deletion must not silently fall back to an arbitrary order.
    We only delete an explicitly selected order.
    """

    if not order_id:
        raise ValidationError("No specific order was selected for deletion.")

    return get_order_by_id(
        order_id=order_id,
        customer=customer,
    )


def _build_order_create_context(order) -> str:
    items = list(
        order.items.filter(
            is_deleted=False,
        )
        .select_related(
            "product",
            "product__category",
        )
        .order_by("id")
    )

    if not items:
        return (
            "A pending order was created, but " "its order items could not be loaded."
        )

    lines = [
        "A new pending order draft has been created successfully.",
        "",
        f"Order ID: {order.id}",
        f"Order status: {order.get_status_display()}",
        f"Total amount: {order.total_amount}",
        "",
        "Order items:",
    ]

    for index, item in enumerate(
        items,
        start=1,
    ):
        lines.extend(
            [
                f"{index}. {item.product.name}",
                f"   Quantity: {item.quantity}",
                f"   Price per item: {item.price_at_order}",
                f"   Subtotal: {item.subtotal}",
            ]
        )

    lines.extend(
        [
            "",
            (
                "The order is currently PENDING and waiting "
                "for customer confirmation."
            ),
            "Ask the customer to confirm the order.",
            "Do not claim that the order is confirmed yet.",
        ]
    )

    return "\n".join(lines).strip()


def _build_order_confirmation_context(order) -> str:
    return f"""
The customer successfully confirmed the order.

Order ID:
{order.id}

Current status:
{order.get_status_display()}

Total amount:
{order.total_amount}

The order is now CONFIRMED.

Tell the customer that the order has been confirmed and provide the exact
Order ID so they can use it later to ask for the order status or details.

Do not change the order status further.
The manager controls the next operational status.
""".strip()


def _build_order_status_context(order) -> str:
    return f"""
CURRENT AUTHORITATIVE ORDER STATUS:

Order ID:
{order.id}

Status:
{order.get_status_display()}

Status code:
{order.status}

Total amount:
{order.total_amount}

Created at:
{order.created_at}

IMPORTANT:
Use the exact current status provided above.
Do not reinterpret, replace, or infer a different status.
""".strip()


def _build_order_list_context(orders) -> str:
    orders = list(orders)

    if not orders:
        return "The customer currently has no orders available for this store."

    lines = ["Customer orders:"]

    for index, order in enumerate(orders, start=1):
        lines.extend(
            [
                f"Order {index}:",
                f"Order ID: {order.id}",
                f"Status: {order.get_status_display()}",
                f"Total amount: {order.total_amount}",
                f"Created at: {order.created_at}",
                "",
            ]
        )

    lines.append(
        "Ask the customer to provide an Order ID "
        "if they want details about a specific order."
    )

    return "\n".join(lines)


def _build_order_details_context(order) -> str:
    """
    Build complete customer-safe order details.

    Includes:
    - Order-level information
    - Every active OrderItem
    - Customer-safe Product information
    """

    lines = [
        "FULL ORDER DETAILS:",
        "",
        f"Order ID: {order.id}",
        f"Status: {order.get_status_display()}",
        ("Payment method: " f"{order.get_payment_method_display()}"),
        f"Paid: {'Yes' if order.is_paid else 'No'}",
        f"Total amount: {order.total_amount}",
        f"Created at: {order.created_at}",
    ]

    if order.notes:
        lines.append(f"Notes: {order.notes}")

    lines.extend(
        [
            "",
            "PRODUCT DETAILS:",
        ]
    )

    items = list(
        order.items.filter(
            is_deleted=False,
        )
        .select_related(
            "product",
            "product__category",
        )
        .order_by("id")
    )

    if not items:
        lines.append("No active order items were found.")
        return "\n".join(lines)

    for index, item in enumerate(items, start=1):
        product = item.product

        category_name = product.category.name if product.category_id else "Unknown"

        price = getattr(
            product,
            "price",
            None,
        )

        discount_price = getattr(
            product,
            "discount_price",
            None,
        )

        final_price = getattr(
            product,
            "final_price",
            None,
        )

        is_out_of_stock = getattr(
            product,
            "is_out_of_stock",
            None,
        )

        lines.extend(
            [
                "",
                f"Product {index}:",
                f"Name: {product.name}",
                f"Category: {category_name}",
                f"SKU: {product.sku or 'Not available'}",
                (
                    "Description: "
                    f"{product.description or 'No description available'}"
                ),
                (
                    "Regular price: "
                    f"{price if price is not None else 'Not available'}"
                ),
                (
                    "Discount price: "
                    f"{discount_price if discount_price is not None else 'None'}"
                ),
                (
                    "Current final price: "
                    f"{final_price if final_price is not None else 'Not available'}"
                ),
                ("Out of stock: " f"{'Yes' if is_out_of_stock else 'No'}"),
                f"Price at order: {item.price_at_order}",
                f"Subtotal: {item.subtotal}",
            ]
        )

    lines.extend(
        [
            "",
            (
                "Include all available details for every product in the order "
                "Always show the product name and description "
                "Include all other available product fields "
                "Clearly show whether each product is available or out of stock "
                "Always show the original price for each product "
                "Always show the discounted price when available "
                "Keep all product prices exactly as provided."
            ),
        ]
    )

    return "\n".join(lines)


def _build_order_clarification_context(clarification_message: str) -> str:
    return f"""
The customer wants to create an order, but the order cannot be created yet.

Reason:
{clarification_message}

Ask the customer for the missing or unclear product details before creating the order.
""".strip()


def _build_order_modification_context(order, modification_type) -> str:
    return f"""
The customer's existing order was successfully modified.

Order ID:
{order.id}

Modification:
{modification_type}

Current status:
{order.get_status_display()}

Updated total:
{order.total_amount}

IMPORTANT:
The order is now PENDING and requires customer confirmation again.

Show the customer the updated order summary and ask for confirmation.
Do not claim that the modified order is confirmed.
""".strip()


def _build_order_delete_confirmation_context(order) -> str:
    return f"""
DELETE CONFIRMATION REQUIRED.

The customer requested deletion of the following order.

{_build_order_details_context(order)}

IMPORTANT:
The order has NOT been deleted yet.

The customer must explicitly confirm the deletion.

Ask:
"Are you sure you want to delete this order?"

Do not claim that the order was deleted yet.
""".strip()


def _build_order_deleted_context(order) -> str:
    return f"""
The order was successfully deleted using soft deletion.

Order ID:
{order.id}

IMPORTANT:
The order record and its historical data remain preserved in the database,
but the order is no longer considered active.

Tell the customer that the order was deleted successfully.
""".strip()


def _build_order_delete_cancelled_context(orders) -> str:
    orders_context = _build_order_list_context(orders)

    return f"""
The customer did NOT confirm deletion of the previously selected order.

Do not delete any order.

Tell the customer that the deletion was cancelled.

Then show the active order list and ask which order they mean.

Customer orders:
{orders_context}
""".strip()


def _build_order_edit_blocked_context(order) -> str:
    return f"""
The customer attempted to modify or delete an order that cannot
currently be changed.

Order ID:
{order.id}

Current status:
{order.get_status_display()}

The order is already beyond the editable stage.

Tell the customer naturally that unfortunately the order cannot
be modified or deleted because it is already in the delivery process.

Do not claim that any modification or deletion was performed.
""".strip()


def _build_order_item_resolution_context(item_request):
    semantic_query = (
        getattr(
            item_request,
            "semantic_query",
            "",
        )
        or ""
    ).strip()

    if not semantic_query:
        raise ValidationError("The product to modify was not identified.")

    filters = getattr(
        item_request,
        "filters",
        None,
    )

    if filters is None:
        filters = SearchFilters(
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

    return semantic_query, filters


def _resolve_modification_product(customer, item_request):
    semantic_query, filters = _build_order_item_resolution_context(item_request)

    resolution = resolve_product_for_order(
        customer=customer,
        semantic_query=semantic_query,
        filters=filters,
        limit=5,
    )

    if resolution.product:
        return resolution.product

    if resolution.candidates:
        candidates = "\n".join(
            f"{index}. {product.name}"
            for index, product in enumerate(
                resolution.candidates,
                start=1,
            )
        )

        raise ValidationError(
            (
                f"Multiple products matched "
                f"'{semantic_query}'.\n"
                f"{candidates}\n"
                "Ask the customer to choose the exact product."
            )
        )

    raise ValidationError(
        resolution.reason or (f"No matching product was found for '{semantic_query}'.")
    )


def handle_pending_delete_confirmation(conversation_id, customer, customer_message):
    """
    Resolve a pending destructive delete confirmation.

    Returns:
        str | None

        None means there is no pending delete confirmation.
    """

    pending_order_id = _get_pending_delete_confirmation(conversation_id)

    if not pending_order_id:
        return None

    decision = _parse_delete_confirmation(customer_message)

    if decision == "confirm":

        _clear_pending_delete_confirmation(conversation_id)

        try:
            order = get_order_by_id(
                order_id=pending_order_id,
                customer=customer,
            )

            deleted_order = soft_delete_order(
                order=order,
                customer=customer,
            )

        except ValidationError:

            try:
                order = get_order_by_id(
                    order_id=pending_order_id,
                    customer=customer,
                )
            except ValidationError:
                return (
                    "The order could not be deleted because "
                    "it is no longer available."
                )

            if order.status in EDIT_BLOCKED_STATUSES:
                return _build_order_edit_blocked_context(order)

            return (
                "The order could not be deleted. "
                "Do not claim that the deletion succeeded."
            )
        else:
            _clear_current_order(conversation_id)

            return _build_order_deleted_context(deleted_order)

    if decision == "cancel":

        _clear_pending_delete_confirmation(conversation_id)

        orders = get_customer_orders(
            customer=customer,
            limit=CUSTOMER_ORDERS_LIMIT,
        )

        return _build_order_delete_cancelled_context(orders)

    pending_order = get_order_by_id(
        order_id=pending_order_id,
        customer=customer,
    )

    return f"""
DELETE CONFIRMATION IS STILL REQUIRED.

Selected order:

{_build_order_details_context(pending_order)}

The order has NOT been deleted.

Ask the customer clearly whether they want to delete this order.
Do not perform deletion without explicit confirmation.
""".strip()


def handle_order_create(customer, query_plan, store):
    """
    Create or extend a PENDING order draft.
    """

    requested_items = list(
        getattr(
            query_plan,
            "order_items",
            [],
        )
        or []
    )

    if (
        not requested_items
        and getattr(
            query_plan,
            "semantic_query",
            "",
        ).strip()
    ):
        requested_items = [
            SimpleNamespace(
                semantic_query=query_plan.semantic_query,
                quantity=None,
                min_price=getattr(
                    query_plan.filters,
                    "min_price",
                    None,
                ),
                max_price=getattr(
                    query_plan.filters,
                    "max_price",
                    None,
                ),
                category_id=getattr(
                    query_plan.filters,
                    "category_id",
                    None,
                ),
            )
        ]

    if not requested_items:
        return _build_order_clarification_context(
            "No order items were provided for the order request."
        )

    pending_order = get_latest_pending_order(customer)

    try:
        result = build_pending_order_draft(
            customer=customer,
            order_items=requested_items,
            pending_order=pending_order,
        )

    except ValidationError as exc:
        return _build_order_clarification_context(str(exc))

    if result.clarification_needed:
        return _build_order_clarification_context(result.clarification_message)

    if not result.order:
        return _build_order_clarification_context("The order could not be created.")

    _set_current_order(
        conversation_id=getattr(query_plan, "conversation_id", None) or "",
        order_id=result.order.id,
    )

    return _build_order_create_context(result.order)


def handle_order_confirmation(customer):
    """
    Confirm the customer's latest PENDING order.
    """

    pending_order = get_latest_pending_order(customer)

    if not pending_order:
        return "No pending order was found for the current customer."

    try:
        order = confirm_order(
            order=pending_order,
            customer=customer,
        )

    except ValidationError as exc:
        return f"Order could not be confirmed: {exc}"

    return _build_order_confirmation_context(order)


def handle_order_status(customer, order_id):
    """
    Retrieve the current status of a specific order.
    """

    if not order_id:
        return (
            "The customer asked for an order status "
            "but did not provide an Order UUID."
        )

    try:
        order = get_order_by_id(
            order_id=order_id,
            customer=customer,
        )

    except ValidationError as exc:
        return f"Order status could not be retrieved: {exc}"

    return _build_order_status_context(order)


def handle_order_list(customer):
    """
    Retrieve the customer's recent orders.
    """

    orders = list(
        get_customer_orders(
            customer=customer,
            limit=CUSTOMER_ORDERS_LIMIT,
        )
    )

    if not orders:
        return "The customer currently has no active orders."

    return _build_order_list_context(orders)


def handle_order_details(customer, order_id, conversation_id=None):
    """
    Retrieve full order details.

    If an Order UUID is provided:
        retrieve that exact order.

    If no UUID is provided:
        prefer the current order stored for the conversation,
        then the latest PENDING order,
        then the latest active customer order.
    """

    try:
        if order_id:
            order = get_order_by_id(
                order_id=order_id,
                customer=customer,
            )
        else:
            current_order_id = None
            if conversation_id is not None:
                current_order_id = _get_current_order(conversation_id)

            if current_order_id:
                try:
                    order = get_order_by_id(
                        order_id=current_order_id,
                        customer=customer,
                    )
                except ValidationError:
                    order = None
            else:
                order = None

            if order is None:
                order = _get_target_order(
                    customer=customer,
                    order_id=None,
                )

    except ValidationError as exc:
        return f"Order details could not be retrieved: {exc}"

    if conversation_id is not None and order:
        _set_current_order(
            conversation_id=conversation_id,
            order_id=order.id,
        )

    return _build_order_details_context(order)


def handle_order_modify(customer, query_plan, conversation_id=None):
    """
    Modify an existing order.

    Supported:
    - add_item
    - update_quantity
    - remove_item

    A successful modification moves the order back to PENDING.
    The customer must confirm the modified order again.
    """

    modification_type = (
        getattr(
            query_plan,
            "modification_type",
            None,
        )
        or ""
    ).strip()

    if modification_type not in {
        "add_item",
        "update_quantity",
        "remove_item",
    }:
        return "The requested order modification type was not identified."

    raw_customer_message = (
        getattr(
            query_plan,
            "customer_message",
            "",
        )
        or ""
    )

    explicit_order_id = _extract_order_uuid(raw_customer_message)

    try:
        order = _get_target_order(
            customer=customer,
            order_id=explicit_order_id
            or getattr(
                query_plan,
                "order_id",
                None,
            ),
        )

    except ValidationError as exc:
        return f"Order modification could not be started: {exc}"

    order_items = list(
        getattr(
            query_plan,
            "order_items",
            [],
        )
        or []
    )

    if not order_items:
        return (
            "The customer requested an order modification, "
            "but no product item was identified."
        )

    try:

        with transaction.atomic():

            if modification_type == "add_item":

                for item_request in order_items:

                    product = _resolve_modification_product(
                        customer=customer,
                        item_request=item_request,
                    )

                    quantity = getattr(
                        item_request,
                        "quantity",
                        None,
                    )

                    if quantity is None:
                        raise ValidationError(
                            f"Quantity is required for '{product.name}'."
                        )

                    add_item_to_existing_order(
                        order=order,
                        customer=customer,
                        product=product,
                        quantity=quantity,
                    )

            elif modification_type == "update_quantity":

                for item_request in order_items:

                    product = _resolve_modification_product(
                        customer=customer,
                        item_request=item_request,
                    )

                    quantity = getattr(
                        item_request,
                        "quantity",
                        None,
                    )

                    if quantity is None:
                        raise ValidationError(
                            f"New quantity is required for '{product.name}'."
                        )

                    update_existing_order_item_quantity(
                        order=order,
                        customer=customer,
                        product=product,
                        quantity=quantity,
                    )

            elif modification_type == "remove_item":

                for item_request in order_items:

                    product = _resolve_modification_product(
                        customer=customer,
                        item_request=item_request,
                    )

                    remove_item_from_existing_order(
                        order=order,
                        customer=customer,
                        product=product,
                    )

            order = get_order_by_id(
                order_id=order.id,
                customer=customer,
            )

            if conversation_id is not None:
                _set_current_order(
                    conversation_id=conversation_id,
                    order_id=order.id,
                )

    except ValidationError as exc:

        current_order = order

        if current_order.status in EDIT_BLOCKED_STATUSES:
            return _build_order_edit_blocked_context(current_order)

        return (
            "The order could not be modified.\n\n"
            f"Reason:\n{exc}\n\n"
            "Do not claim that the order was modified."
        )

    return _build_order_modification_context(
        order=order,
        modification_type=modification_type,
    )


def handle_order_delete(
    customer,
    order_id,
    conversation_id,
):
    """
    Start a safe order deletion flow.

    The order is NOT deleted immediately.

    First:
    - resolve the order
    - check whether it is editable
    - store a pending delete confirmation in Redis
    - show full order details
    - ask for explicit confirmation
    """

    raw_order_id = order_id

    if not raw_order_id and conversation_id is not None:
        raw_order_id = _get_current_order(conversation_id)

    try:
        order = _get_delete_target_order(
            customer=customer,
            order_id=raw_order_id,
        )

    except ValidationError as exc:
        return f"Order could not be selected for deletion: {exc}"

    if order.status in EDIT_BLOCKED_STATUSES:
        return _build_order_edit_blocked_context(order)

    _set_pending_delete_confirmation(
        conversation_id=conversation_id,
        order_id=order.id,
    )

    _set_current_order(
        conversation_id=conversation_id,
        order_id=order.id,
    )

    return _build_order_delete_confirmation_context(order)


def handle_order_request(
    store, customer, query_plan, conversation_id=None, customer_message=""
):
    """
    Route all order-related requests.
    """

    request_type = query_plan.request_type

    explicit_uuid = _extract_order_uuid(customer_message)
    explicit_uuid_prefix = _extract_order_uuid_prefix(customer_message)

    if not explicit_uuid:
        if explicit_uuid_prefix:
            matching_orders = list(
                Order.objects.filter(
                    customer=customer, id__startswith=explicit_uuid_prefix
                )[:2]
            )

            if len(matching_orders) == 1:
                explicit_uuid = str(matching_orders[0].id)

    if explicit_uuid:
        query_plan.order_id = explicit_uuid

    if request_type == "order_create":
        return handle_order_create(
            customer=customer,
            query_plan=query_plan,
            store=store,
        )

    if request_type == "order_modify":
        return handle_order_modify(
            customer=customer,
            query_plan=query_plan,
            conversation_id=conversation_id,
        )

    if request_type == "order_delete":
        if not conversation_id:
            return (
                "The conversation ID is required " "to safely process order deletion."
            )

        return handle_order_delete(
            customer=customer,
            order_id=query_plan.order_id,
            conversation_id=conversation_id,
        )

    if request_type == "order_confirmation":
        return handle_order_confirmation(
            customer=customer,
        )

    if request_type == "order_status":
        return handle_order_status(
            customer=customer,
            order_id=query_plan.order_id,
        )

    if request_type == "order_list":
        return handle_order_list(
            customer=customer,
        )

    if request_type == "order_details":
        return handle_order_details(
            customer=customer,
            order_id=query_plan.order_id,
            conversation_id=conversation_id,
        )

    return ""
