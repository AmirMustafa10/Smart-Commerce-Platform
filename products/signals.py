from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from .tasks import sync_product_embedding_task


@receiver(post_save, sender=Product, dispatch_uid="products.sync_product_embedding")
def product_saved(sender, instance, **kwargs):
    transaction.on_commit(
        lambda product_id=instance.pk: (sync_product_embedding_task.delay(product_id))
    )
