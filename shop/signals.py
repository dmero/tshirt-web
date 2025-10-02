"""
Django signals for automatic email notifications on order status changes
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order
from .emails import send_order_shipped_email, send_order_delivered_email
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """
    Track when order status changes to trigger appropriate actions
    """
    if instance.pk:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def send_status_change_email(sender, instance, created, **kwargs):
    """
    Send email notification when order status changes to 'shipped' or 'delivered'
    """
    # Don't send emails for newly created orders (handled elsewhere)
    if created:
        return
    
    # Get old status from the instance (set in pre_save)
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status
    
    # Send shipped email
    if old_status != 'shipped' and new_status == 'shipped':
        logger.info(f"Order #{instance.id} status changed to shipped. Sending email...")
        try:
            send_order_shipped_email(
                order=instance,
                tracking_number=instance.tracking_number,
                tracking_url=instance.tracking_url
            )
        except Exception as e:
            logger.error(f"Failed to send shipped email for order #{instance.id}: {str(e)}")
    
    # Send delivered email
    elif old_status != 'delivered' and new_status == 'delivered':
        logger.info(f"Order #{instance.id} status changed to delivered. Sending email...")
        try:
            send_order_delivered_email(order=instance)
        except Exception as e:
            logger.error(f"Failed to send delivered email for order #{instance.id}: {str(e)}")
