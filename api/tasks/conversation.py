import os
from math import ceil
import requests
from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from model_conversation.models import (
    ChatMessage,
    Conversation,
)
from model_conversation.services.conversation_context import (
    build_conversation_context,
)
from model_conversation.services.response_generator import (
    generate_final_response,
)
from orders.services.order_queries import (
    get_latest_customer_order,
    get_latest_pending_order,
)
from products.models import Category
from products.services.query_planner import (
    QueryPlan,
    create_query_plan,
)

from .orders import (
    handle_order_request,
    handle_pending_delete_confirmation,
)
from .products import (
    handle_broad_catalog_request,
    handle_category_overview,
    handle_product_search,
)

LOCK_TTL_SECONDS = 120
DEBOUNCE_SECONDS = 3


def _get_store_categories(store) -> list[dict]:
    return list(
        Category.objects.filter(store=store).values(
            "id",
            "name",
            "description",
        )
    )


def _send_whatsapp_message(store, to_number: str, message_text: str):
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    access_token = os.getenv("WHATSAPP_API_TOKEN")

    if not phone_number_id:
        raise ValueError(f"Store {store.id} does not have a WhatsApp Phone Number ID.")

    if not access_token:
        raise ValueError("Missing WHATSAPP_API_TOKEN.")

    normalized_to = str(to_number).lstrip("+")

    api_version = os.getenv(
        "WHATSAPP_GRAPH_API_VERSION",
        "v26.0",
    )

    url = f"https://graph.facebook.com/" f"{api_version}/" f"{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": normalized_to,
        "type": "text",
        "text": {
            "body": message_text,
        },
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    print(f"📤 WhatsApp response: " f"{response.status_code} - " f"{response.text}")

    response.raise_for_status()

    return response


def _mark_conversation_idle(conversation_id):
    with transaction.atomic():
        conversation = (
            Conversation.objects.select_for_update().filter(id=conversation_id).first()
        )

        if not conversation:
            return

        conversation.status = Conversation.STATUS_CHOICES.IDLE

        conversation.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )


def _build_active_order_context(customer) -> str:
    """
    Build authoritative context about the customer's latest relevant order.
    """

    order = get_latest_pending_order(customer)

    if not order:
        order = get_latest_customer_order(customer)

    if not order:
        return (
            "ACTIVE ORDER CONTEXT:\n"
            "No active or recent order was found "
            "for the current customer."
        )

    lines = [
        "ACTIVE ORDER CONTEXT:",
        f"Order ID: {order.id}",
        f"Status: {order.get_status_display()}",
        f"Total amount: {order.total_amount}",
        "Items:",
    ]

    items = list(
        order.items.filter(is_deleted=False)
        .select_related(
            "product",
            "product__category",
        )
        .order_by("id")
    )

    if not items:
        lines.append("- No active order items.")
    else:
        for index, item in enumerate(items, start=1):
            category_name = (
                item.product.category.name if item.product.category_id else "Unknown"
            )

            lines.append(
                (
                    f"- Item {index}: "
                    f"{item.product.name} | "
                    f"Category: {category_name} | "
                )
            )

    lines.extend(
        [
            "",
            "IMPORTANT:",
            "This is authoritative current order data from the database.",
            "Use it to resolve references to the customer's current/recent order.",
            "Do not invent products or order items that are not listed here.",
        ]
    )

    return "\n".join(lines)


def _format_planner_context(
    conversation_context: dict, current_user_message: str, active_order_context: str
) -> str:
    """
    Build planner context with explicit priority:

    1. Current customer message
    2. Immediate recent context
    3. Active order database context
    4. Older recent history
    5. Conversation summary
    """

    recent_messages = list(
        conversation_context.get(
            "recent_messages",
            [],
        )
    )

    summary = (
        conversation_context.get(
            "summary",
            "",
        )
        or "No conversation summary is available."
    )

    immediate_messages = recent_messages[-4:]
    older_messages = recent_messages[:-4]

    lines = [
        "CURRENT CUSTOMER MESSAGE:",
        current_user_message.strip(),
        "",
        "IMMEDIATE CONVERSATION CONTEXT:",
    ]

    if immediate_messages:
        for message in immediate_messages:
            role = message.get(
                "role",
                "Unknown",
            )

            text = message.get(
                "text",
                "",
            ).strip()

            if text:
                lines.append(f"{role}: {text}")
    else:
        lines.append("No immediate conversation context.")

    lines.extend(
        [
            "",
            active_order_context,
            "",
            "OLDER RECENT CONVERSATION HISTORY:",
        ]
    )

    if older_messages:
        for message in older_messages:
            role = message.get(
                "role",
                "Unknown",
            )

            text = message.get(
                "text",
                "",
            ).strip()

            if text:
                lines.append(f"{role}: {text}")
    else:
        lines.append("No older recent conversation history.")

    lines.extend(
        [
            "",
            "LONG-TERM CONVERSATION SUMMARY:",
            summary,
        ]
    )

    return "\n".join(lines)


def _build_business_context(store) -> str:
    return f"""
Business name:
{store.name}

Business description:
{"No business description is available."}

Payment methods:
- Cash on Delivery: Available
- Visa: Coming Soon

Payment rule:
Do not claim that Visa is currently available.
Do not invent any additional payment methods.
""".strip()


@shared_task(name="api.tasks.process_conversation_task")
def process_conversation_task(conversation_id):
    """
    Main conversation orchestration task.
    """

    lock_key = f"whatsflow:" f"conversation-lock:" f"{conversation_id}"

    if not cache.add(lock_key, "1", timeout=LOCK_TTL_SECONDS):
        print(f"🔒 Conversation " f"{conversation_id} " f"is already locked.")

        return "locked"

    try:
        while True:

            # =============================================
            # 1. Load conversation
            # =============================================

            with transaction.atomic():
                conversation = (
                    Conversation.objects.select_for_update()
                    .select_related(
                        "customer",
                        "store",
                    )
                    .get(id=conversation_id)
                )

                conversation.status = Conversation.STATUS_CHOICES.PROCESSING

                conversation.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                latest_user_message = (
                    ChatMessage.objects.filter(
                        conversation=conversation,
                        sender=(ChatMessage.SENDER_CHOICES.USER),
                    )
                    .order_by("-id")
                    .first()
                )

                if not latest_user_message:
                    conversation.status = Conversation.STATUS_CHOICES.IDLE

                    conversation.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                    return "no-user-messages"

                # =========================================
                # 2. Debounce
                # =========================================

                elapsed_seconds = (
                    timezone.now() - latest_user_message.timestamp
                ).total_seconds()

                if elapsed_seconds < DEBOUNCE_SECONDS:
                    remaining = max(
                        1,
                        ceil(DEBOUNCE_SECONDS - elapsed_seconds),
                    )

                    print(
                        f"⏳ Conversation "
                        f"{conversation_id} "
                        f"still receiving messages. "
                        f"Rescheduling in "
                        f"{remaining}s..."
                    )

                    process_conversation_task.apply_async(
                        args=[conversation_id],
                        countdown=remaining,
                    )

                    conversation.status = Conversation.STATUS_CHOICES.IDLE

                    conversation.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                    return "debounced"

                # =========================================
                # 3. Collect pending messages
                # =========================================

                pending_messages = list(
                    ChatMessage.objects.filter(
                        conversation=conversation,
                        sender=(ChatMessage.SENDER_CHOICES.USER),
                        id__gt=(conversation.last_processed_user_message_id),
                    ).order_by("id")
                )

                if not pending_messages:
                    conversation.status = Conversation.STATUS_CHOICES.IDLE

                    conversation.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                    return "no-pending-messages"

                current_message_id = pending_messages[-1].id

                current_user_message = "\n".join(
                    message.text.strip()
                    for message in pending_messages
                    if message.text.strip()
                ).strip()

                # =========================================
                # 4. Conversation Context
                # =========================================

                conversation_context = build_conversation_context(
                    conversation=conversation,
                    before_message_id=(pending_messages[0].id),
                )

                # =========================================
                # 5. Store + Customer
                # =========================================

                store = conversation.store
                customer = conversation.customer

                store_categories = _get_store_categories(store)

            # =================================================
            # External calls happen outside DB transaction.
            # =================================================

            # =============================================
            # 6. Handle pending destructive action FIRST
            # =============================================

            pending_action_context = handle_pending_delete_confirmation(
                conversation_id=conversation_id,
                customer=customer,
                customer_message=current_user_message,
            )

            if pending_action_context is not None:
                query_plan = None
                retrieved_business_context = pending_action_context

            else:
                # =========================================
                # 7. Active Order Context
                # =========================================

                active_order_context = _build_active_order_context(customer)

                # =========================================
                # 8. Gemini #1 → Query Plan
                # =========================================

                planner_message = _format_planner_context(
                    conversation_context=(conversation_context),
                    current_user_message=(current_user_message),
                    active_order_context=(active_order_context),
                )

                query_plan = create_query_plan(
                    customer_message=planner_message,
                    categories=store_categories,
                    store_name=store.name,
                    store_description="",
                )

                print(
                    f"🧠 Query plan for conversation "
                    f"{conversation_id}: "
                    f"{query_plan}"
                )

                # =========================================
                # 9. Request Routing
                # =========================================

                if query_plan.request_type == "product_search":
                    retrieved_business_context = handle_product_search(
                        store=store,
                        query_plan=query_plan,
                    )

                elif query_plan.request_type == "product_clarification":
                    retrieved_business_context = """
The customer is interested in a product, but the request
is currently too broad for a useful product search.

Do NOT retrieve or enumerate products.

Ask one concise clarification question.

Useful clarification dimensions may include:
- preferred brand
- budget
- storage
- RAM
- intended use
- important features

Only ask for information relevant to the customer's
current product request.
""".strip()

                elif query_plan.request_type == "category_overview":
                    retrieved_business_context = handle_category_overview(
                        store_categories=(store_categories),
                    )

                elif query_plan.request_type == "broad_catalog_request":
                    retrieved_business_context = handle_broad_catalog_request()

                elif query_plan.request_type in {
                    "order_create",
                    "order_modify",
                    "order_delete",
                    "order_confirmation",
                    "order_status",
                    "order_list",
                    "order_details",
                }:
                    retrieved_business_context = handle_order_request(
                        query_plan=query_plan,
                        store=store,
                        customer=customer,
                        conversation_id=conversation_id,
                        customer_message=current_user_message,
                    )

                else:
                    retrieved_business_context = (
                        "No product, category, or order retrieval is required."
                    )

            # =============================================
            # 10. Business Context
            # =============================================

            business_context = _build_business_context(
                store=store,
            )

            # =============================================
            # 11. Gemini #2 → Final Response
            # =============================================

            if query_plan is None:
                query_plan = QueryPlan(
                    request_type="order_delete",
                    search_required=False,
                    semantic_query="",
                    order_id=None,
                    modification_type=None,
                    order_items=[],
                )

            final_reply = generate_final_response(
                store_name=store.name,
                store_description="",
                business_context=business_context,
                conversation_context=(conversation_context),
                current_user_message=(current_user_message),
                query_plan=query_plan,
                retrieved_business_context=(retrieved_business_context),
            )

            if not final_reply:
                final_reply = "Sorry, I couldn't generate a response right now."

            # =============================================
            # 12. Check for newer messages
            # =============================================

            with transaction.atomic():
                conversation = (
                    Conversation.objects.select_for_update()
                    .select_related(
                        "customer",
                        "store",
                    )
                    .get(id=conversation_id)
                )

                latest_user_message_id_now = (
                    ChatMessage.objects.filter(
                        conversation=conversation,
                        sender=(ChatMessage.SENDER_CHOICES.USER),
                    )
                    .order_by("-id")
                    .values_list(
                        "id",
                        flat=True,
                    )
                    .first()
                )

                if (
                    latest_user_message_id_now
                    and latest_user_message_id_now > current_message_id
                ):
                    print(
                        f"♻️ Newer message arrived for "
                        f"conversation "
                        f"{conversation_id}. "
                        f"Discarding stale response "
                        f"and re-processing."
                    )

                    continue

                # =========================================
                # 13. Save AI response
                # =========================================

                ChatMessage.objects.create(
                    conversation=conversation,
                    sender=(ChatMessage.SENDER_CHOICES.MODEL),
                    text=final_reply,
                )

                conversation.last_processed_user_message_id = current_message_id

                conversation.status = Conversation.STATUS_CHOICES.IDLE

                conversation.save(
                    update_fields=[
                        "last_processed_user_message_id",
                        "status",
                        "updated_at",
                    ]
                )

                customer_phone = conversation.customer.phone_number
                store = conversation.store

            # =============================================
            # 14. Send WhatsApp response
            # =============================================

            _send_whatsapp_message(
                store=store,
                to_number=customer_phone,
                message_text=final_reply,
            )

            print(f"✅ Conversation " f"{conversation_id} " f"completed.")

            return "success"

    except Exception as exc:
        print(f"❌ Conversation task error " f"{conversation_id}: {exc}")

        _mark_conversation_idle(conversation_id)

        raise

    finally:
        cache.delete(lock_key)
