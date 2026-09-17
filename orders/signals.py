from django.db.models.signals import pre_delete, pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from .models import OrderItem, Order
from products.models import Product


@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """Update the total amount of the order when an item is saved or deleted."""
    order = instance.order
    aggregation = order.items.aggregate(total=Sum(F("quantity") * F("price_at_order")))

    total = aggregation["total"] or 0.00
    order.total_amount = total
    order.save(update_fields=["total_amount"])


@receiver(post_save, sender=OrderItem)
def deduct_stock_on_create(sender, instance, created, **kwargs):
    """When a new product is added to the order, we deduct the quantity from the inventory."""
    if created:
        Product.objects.filter(pk=instance.product_id).update(
            stock_quantity=F("stock_quantity") - instance.quantity
        )


@receiver(pre_save, sender=OrderItem)
def adjust_stock_on_update(sender, instance, **kwargs):
    """If the merchant adjusts the quantity, we calculate the difference and either deduct it or return it to the warehouse."""
    if not instance._state.adding:  # If this is a modification to an existing product
        try:
            old_item = OrderItem.objects.get(pk=instance.pk)
            difference = instance.quantity - old_item.quantity

            if difference != 0:
                Product.objects.filter(pk=instance.product_id).update(
                    stock_quantity=F("stock_quantity") - difference
                )
        except OrderItem.DoesNotExist:
            pass


@receiver(post_delete, sender=OrderItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    """When a product is removed from the order (Hard Delete), we return the quantity to the warehouse."""
    Product.objects.filter(pk=instance.product_id).update(
        stock_quantity=F("stock_quantity") + instance.quantity
    )


@receiver(pre_save, sender=Order)
def manage_stock_on_order_status_change(sender, instance, **kwargs):
    """
    Monitor order status and soft-delete changes.
    If the status changes to "Cancelled" or "Returned," OR if it gets soft-deleted, return the goods.
    If it reverts to "In Progress" or "Confirmed" (and is not deleted), deduct the goods again.
    """
    if not instance._state.adding and instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            inactive_statuses = [Order.Status.CANCELLED, Order.Status.RETURNED]

            # Treat the order as inactive if its status is cancelled/returned OR if it is soft-deleted
            old_is_inactive = (
                old_order.status in inactive_statuses
            ) or old_order.is_deleted
            new_is_inactive = (
                instance.status in inactive_statuses
            ) or instance.is_deleted

            # Scenario 1: The order was active and became inactive -> We restock the goods (+)
            if not old_is_inactive and new_is_inactive:
                for item in instance.items.all():
                    Product.objects.filter(pk=item.product_id).update(
                        stock_quantity=F("stock_quantity") + item.quantity
                    )

            # Scenario 2 is REMOVED completely because Order.clean() blocks it.
        except Order.DoesNotExist:
            pass


@receiver(pre_delete, sender=OrderItem)
def prevent_deleting_frozen_items(sender, instance, **kwargs):
    """
    Deleting any product is prohibited if the order is closed or out for delivery.
    """
    frozen_statuses = [
        Order.Status.SHIPPED,
        Order.Status.DELIVERED,
        Order.Status.CANCELLED,
        Order.Status.RETURNED,
    ]
    if instance.order.status in frozen_statuses:
        raise ValidationError(
            f"Products cannot be deleted from an order with the status '{instance.order.get_status_display()}'."
        )
