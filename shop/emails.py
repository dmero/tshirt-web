"""
Email utility functions for sending order and refund notifications
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order, request=None):
    """
    Send order confirmation email to customer
    
    Args:
        order: Order instance
        request: HttpRequest instance (optional, for site URL)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get recipient email
        recipient_email = order.customer.user.email
        
        if not recipient_email:
            logger.warning(f"No email address for order #{order.id}")
            return False
        
        # Get site URL
        if request:
            site_url = request.build_absolute_uri('/')[:-1]
        else:
            site_url = 'http://localhost:8000'
        
        # Prepare context
        context = {
            'order': order,
            'site_url': site_url,
        }
        
        # Render email templates
        subject = f'Order Confirmation - Order #{order.id}'
        text_content = render_to_string('shop/emails/order_confirmation.txt', context)
        html_content = render_to_string('shop/emails/order_confirmation.html', context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Order confirmation email sent for order #{order.id} to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for order #{order.id}: {str(e)}")
        return False


def send_refund_confirmation_email(order, request=None):
    """
    Send refund confirmation email to customer
    
    Args:
        order: Order instance
        request: HttpRequest instance (optional, for site URL)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get recipient email
        recipient_email = order.customer.user.email
        
        if not recipient_email:
            logger.warning(f"No email address for order #{order.id}")
            return False
        
        # Get site URL
        if request:
            site_url = request.build_absolute_uri('/')[:-1]
        else:
            site_url = 'http://localhost:8000'
        
        # Prepare context
        context = {
            'order': order,
            'site_url': site_url,
        }
        
        # Render email templates
        subject = f'Refund Processed - Order #{order.id}'
        text_content = render_to_string('shop/emails/refund_confirmation.txt', context)
        html_content = render_to_string('shop/emails/refund_confirmation.html', context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Refund confirmation email sent for order #{order.id} to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send refund confirmation email for order #{order.id}: {str(e)}")
        return False


def send_order_shipped_email(order, request=None, tracking_number=None, tracking_url=None):
    """
    Send order shipped notification email to customer
    
    Args:
        order: Order instance
        request: HttpRequest instance (optional, for site URL)
        tracking_number: Tracking number string (optional)
        tracking_url: URL to track shipment (optional)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get recipient email
        recipient_email = order.customer.user.email
        
        if not recipient_email:
            logger.warning(f"No email address for order #{order.id}")
            return False
        
        # Get site URL
        if request:
            site_url = request.build_absolute_uri('/')[:-1]
        else:
            site_url = 'http://localhost:8000'
        
        # Prepare context
        context = {
            'order': order,
            'site_url': site_url,
            'tracking_number': tracking_number,
            'tracking_url': tracking_url,
        }
        
        # Render email templates
        subject = f'Your Order Has Shipped - Order #{order.id}'
        text_content = render_to_string('shop/emails/order_shipped.txt', context)
        html_content = render_to_string('shop/emails/order_shipped.html', context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Order shipped email sent for order #{order.id} to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order shipped email for order #{order.id}: {str(e)}")
        return False


def send_order_delivered_email(order, request=None):
    """
    Send order delivered notification email to customer
    
    Args:
        order: Order instance
        request: HttpRequest instance (optional, for site URL)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get recipient email
        recipient_email = order.customer.user.email
        
        if not recipient_email:
            logger.warning(f"No email address for order #{order.id}")
            return False
        
        # Get site URL
        if request:
            site_url = request.build_absolute_uri('/')[:-1]
        else:
            site_url = 'http://localhost:8000'
        
        # Prepare context
        context = {
            'order': order,
            'site_url': site_url,
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        # Render email templates
        subject = f'Your Order Has Been Delivered - Order #{order.id}'
        text_content = render_to_string('shop/emails/order_delivered.txt', context)
        html_content = render_to_string('shop/emails/order_delivered.html', context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Order delivered email sent for order #{order.id} to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order delivered email for order #{order.id}: {str(e)}")
        return False
