from django.db import models
from orders.models import Customer


class Conversation(models.Model):
    STATUS_CHOICES = (
        ("idle", "Idle"),
        ("processing", "Processing"),
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="conversations"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="idle")
    summary = models.TextField(
        blank=True,
        null=True,
        help_text="Summary of past conversations",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation with {self.customer.phone_number} - {self.status}"


class ChatMessage(models.Model):
    SENDER_CHOICES = (
        ("user", "Customer"),
        ("model", "AI"),
    )

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"
