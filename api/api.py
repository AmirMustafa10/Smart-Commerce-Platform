import json
import os
from django.db import transaction
from django.http import HttpResponse
from ninja import NinjaAPI
from model_conversation.models import Conversation, ChatMessage
from orders.models import Customer
from stores.models import Store
from .tasks import process_conversation_task

api = NinjaAPI()


@api.get("/webhook")
def verify_webhook(request):
    mode = request.GET.get("hub.mode")
    token = request.GET.get("hub.verify_token")
    challenge = request.GET.get("hub.challenge")

    my_secret_token = os.environ.get("WHATSAPP_VERIFY_TOKEN")

    if mode == "subscribe" and token == my_secret_token:
        print("✅ Webhook Verified Successfully!")
        return HttpResponse(challenge)

    return HttpResponse(
        "Forbidden",
        status=403,
    )


@api.post("/webhook")
def receive_whatsapp_message(request):
    try:
        body = json.loads(request.body)

        if body.get("object") != "whatsapp_business_account":
            return HttpResponse(
                "EVENT_RECEIVED",
                status=200,
            )

        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                messages = value.get("messages", [])

                if not messages:
                    continue

                phone_number = value.get(
                    "metadata",
                    {},
                ).get("display_phone_number")

                if not phone_number:
                    print("⚠️ Missing phone_number " "in webhook payload")
                    continue

                try:
                    store = Store.objects.get(whatsapp_number=f"+{phone_number}")
                except Store.DoesNotExist:
                    print(f"⚠️ No store found for " f"phone_number={phone_number}")
                    continue

                message = messages[0]

                msg_type = message.get("type")
                sender_phone = message.get("from")

                if msg_type != "text":
                    print(f"ℹ️ Unsupported message type: " f"{msg_type}")
                    continue

                text = message["text"]["body"]

                contact_name = ""

                contacts = value.get("contacts", [])

                if contacts:
                    contact_name = contacts[0].get("profile", {}).get("name", "") or ""

                with transaction.atomic():

                    customer, _ = Customer.objects.get_or_create(
                        store=store,
                        phone_number=f"+{sender_phone}",
                        defaults={
                            "name": contact_name,
                        },
                    )

                    if contact_name and customer.name != contact_name:
                        customer.name = contact_name

                        customer.save(update_fields=["name"])

                    conversation, _ = Conversation.objects.get_or_create(
                        store=store,
                        customer=customer,
                        defaults={
                            "status": (Conversation.STATUS_CHOICES.IDLE),
                        },
                    )

                    chat_message = ChatMessage.objects.create(
                        conversation=conversation,
                        sender=ChatMessage.SENDER_CHOICES.USER,
                        text=text,
                    )

                    # Start Celery only after the transaction
                    # has successfully committed.
                    transaction.on_commit(
                        lambda conversation_id=conversation.id: process_conversation_task.apply_async(
                            args=[conversation_id],
                            countdown=3,
                        )
                    )

                print("\n" + "=" * 30)
                print(f"📩 New message from: " f"{sender_phone}")
                print(f"🏪 Store: {store}")
                print(f"💬 Text: {text}")
                print(f"🆔 Message ID: " f"{chat_message.id}")
                print("🚀 Celery task queued")
                print("=" * 30 + "\n")

        return HttpResponse(
            "EVENT_RECEIVED",
            status=200,
        )

    except Exception as e:
        print(f"❌ Error: {e}")

        return HttpResponse(
            "ERROR",
            status=500,
        )
