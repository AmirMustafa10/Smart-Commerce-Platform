from django.db import models
from orders.models import Customer

class ChatMessage(models.Model):
    SENDER_CHOICES = (
        ("user", "Customer"),
        ("model", "AI"),
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(
        max_length=10, choices=SENDER_CHOICES, verbose_name="sender"
    )
    text = models.TextField(verbose_name="text of message")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.get_sender_display()}: {self.text[:30]}..."
