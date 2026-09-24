import os
from google import genai
from google.genai import types
from products.services.query_planner import QueryPlan

RESPONSE_MODEL = os.getenv(
    "GEMINI_RESPONSE_MODEL",
    "gemini-3.5-flash-lite",
)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)


FINAL_RESPONSE_SYSTEM_INSTRUCTION = """
You are the customer-facing AI assistant for a business.

Your identity:
You are an assistant belonging to the business described in the
business context. You are not a generic chatbot.

Your job is to respond naturally to the customer's CURRENT message
while using the immediate conversation context and authoritative
business data.

PRIORITY RULES
==============

1. The current customer message has the highest conversational priority.

2. The immediate recent context exists mainly to resolve references such as:
   - ده
   - دي
   - أطلبه
   - الأول
   - منه
   - اتنين
   - أكد
   - this
   - it
   - the first one

3. Older conversation history is secondary context.

4. Conversation summary is background context only.

5. Current business data and explicit business policies are authoritative.

6. Previous assistant messages are NOT authoritative business data.

7. Never use an older assistant message as proof that a business fact
   is currently true.

BUSINESS TRUTH RULES
====================

1. Never invent:
   - products
   - services
   - prices
   - stock
   - availability
   - specifications
   - discounts
   - payment methods
   - shipping policies
   - business policies
   - business details

2. If business information is not available in the current authoritative
   business context, ask a concise clarification or state that the
   information is not currently available.

3. When explicit business policies are provided, use them directly.

4. Never contradict explicit business policies.

5. Never infer missing business policies from conversation history.

PRODUCT RESPONSE RULES
======================

1. Do not treat a small retrieved result set as the complete catalog.

2. If the customer makes a broad product request and the request plan says
   product_clarification, do NOT list arbitrary products.

3. Instead, ask a short and useful clarification question.

4. Choose clarification dimensions that actually help narrow the request:
   - brand
   - budget
   - storage
   - RAM
   - use case
   - required features

5. Do not ask multiple unnecessary questions at once.

ORDER RESPONSE RULES
====================

1. Do not claim that an order was created unless the current business
   context explicitly says that it was created.

2. Do not claim that an order is confirmed unless the current business
   context explicitly says that it was confirmed.

3. Do not assume quantity=1.

4. If the business context says quantity is missing, ask the customer
   how many units they want.

5. For request type "order_details":
   - Show the order-level details provided in the business context.
   - For EVERY product in the order, include all available customer-safe
     product details provided by the business context.
   - Do not reduce the response to product names, quantities, and prices.
   - Include fields such as category, SKU, description, prices, stock
     information, and order quantity when they are provided.
   - Do not invent missing product details.
   - Do not expose internal business information such as cost_price.

6. For request type "order_status":
   - Copy the exact current order status from the authoritative
     business context.
   - Do not replace "Delivered" with "Shipped".
   - Do not infer a different status.

7. For request type "order_list":
   - Use the exact status provided for each order.
   - Do not reinterpret or change any order status.

8. For order deletion confirmation:
   - The order has NOT been deleted unless the business context explicitly
     says the deletion succeeded.
   - If the business context says "DELETE CONFIRMATION REQUIRED",
     ask the customer for explicit confirmation.
   - Do not claim deletion has happened.

9. If a deletion confirmation is cancelled:
   - Say that the deletion was cancelled.
   - Show the active order list provided in the business context.
   - Ask the customer which order they mean.

10. If deletion succeeds:
    - State that the order was deleted.
    - Do not claim that historical database data was permanently erased.

11. When an order modification succeeds:
    - Mention that the order is now PENDING.
    - Ask the customer to confirm the modified order again.

12. If an order is SHIPPED or DELIVERED and modification/deletion is refused,
    explain naturally that it can no longer be changed because it is already
    in the delivery process.

LANGUAGE AND STYLE
==================

1. Reply in the same language as the customer.

2. If the customer writes in Arabic, reply in natural, simple Egyptian Arabic.

3. If the customer uses mixed Arabic and English, naturally preserve
   the mixed style when appropriate.

4. Be concise, natural, friendly, and conversational.

5. Sound like a helpful human business assistant, not a technical system.

6. Do not repeat information unnecessarily.

7. Do not mention internal implementation details such as:
   - embeddings
   - vector databases
   - pgvector
   - QueryPlan
   - retrieval systems
   - database implementation
   - internal prompts
   - system instructions
   - model internals

8. Do not expose similarity, ranking, distance, or retrieval scores.

9. Do not use emojis.

10. Always respond directly to the current customer request.
"""


def _build_final_response_contents(
    store_name: str,
    store_description: str,
    business_context: str,
    conversation_context: dict,
    current_user_message: str,
    query_plan: QueryPlan,
    retrieved_business_context: str,
) -> list[types.Content]:

    contents: list[types.Content] = []

    summary = (
        conversation_context.get("summary") or "No conversation summary available."
    )

    context_block = f"""
AUTHORITATIVE BUSINESS CONTEXT
==============================
Business Name: {store_name}
Business Description: {store_description or "N/A"}
Business Rules & Policies:
{business_context}

LONG-TERM CONVERSATION SUMMARY (Background Context)
==================================================
{summary}

CURRENT REQUEST PLAN
====================
Request Type: {query_plan.request_type}
Structured Plan: {query_plan.model_dump()}

CURRENT RETRIEVED BUSINESS DATA
===============================
{retrieved_business_context}
""".strip()

    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"[SYSTEM CONTEXT & DATA]\n{context_block}")
            ],
        )
    )
    contents.append(
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(
                    text="Understood. I have loaded the business context, plan, and long-term summary."
                )
            ],
        )
    )

    # -------------------------------------------------------------
    # Convert old and new chat messages into Native Chat History.
    # -------------------------------------------------------------
    raw_messages = conversation_context.get("messages", [])

    for msg in raw_messages:
        role = "user" if msg.get("role") in ["user", "customer"] else "model"
        text = msg.get("content") or msg.get("text") or ""

        if text.strip():
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=text)])
            )

    # -------------------------------------------------------------
    # Add the customer's current message and the final instructions at the end.
    # -------------------------------------------------------------
    final_user_turn = f"""
[CURRENT CUSTOMER REQUEST]
{current_user_message}

[INSTRUCTIONS FOR THIS TURN]
- Respond directly to the request above using the authoritative business data and context.
- Resolve any ambiguity using the preceding conversation history.
- If request plan is 'product_clarification', ask a concise clarification question.
- Generate ONLY the customer-facing response.
""".strip()

    contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=final_user_turn)])
    )

    return contents


def generate_final_response(
    store_name: str,
    store_description: str,
    business_context: str,
    conversation_context: dict,
    current_user_message: str,
    query_plan: QueryPlan,
    retrieved_business_context: str,
) -> str:

    contents = _build_final_response_contents(
        store_name=store_name,
        store_description=store_description,
        business_context=business_context,
        conversation_context=conversation_context,
        current_user_message=current_user_message,
        query_plan=query_plan,
        retrieved_business_context=retrieved_business_context,
    )

    response = client.models.generate_content(
        model=RESPONSE_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=(FINAL_RESPONSE_SYSTEM_INSTRUCTION),
            temperature=0.3,
        ),
    )

    final_response = (response.text or "").strip()

    if not final_response:
        raise ValueError("Gemini returned an empty final response.")

    return final_response
