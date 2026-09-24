from django.db import models
from orders.models import Customer
from stores.models import Store
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        IDLE = "IDLE", _("Idle")
        PROCESSING = "Processing", _("Processing")

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="conversations"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES.choices, default=STATUS_CHOICES.IDLE
    )
    summary = models.TextField(
        blank=True,
        null=True,
        help_text="Summary of past conversations",
    )
    last_processed_user_message_id = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["store", "customer"],
                name="unique_conversation_per_store_customer",
            )
        ]

    def __str__(self):
        return f"{self.store} - {self.customer}"


class ChatMessage(models.Model):
    class SENDER_CHOICES(models.TextChoices):
        USER = "USER", _("Customer")
        MODEL = "MODEL", _("AI")

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES.choices)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp", "id"]

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"
