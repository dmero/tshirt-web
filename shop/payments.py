"""Durable order snapshots and idempotent Stripe completion."""
from collections import Counter
from decimal import Decimal
import logging
import stripe
from django.core.validators import validate_email
from django.db import transaction
from .models import Cart, CartItem, Customer, Order, OrderItem, Product
from .emails import send_order_confirmation_email

logger = logging.getLogger(__name__)


@transaction.atomic
def prepare_order(request, data):
    intent_id = data.get('payment_intent_id', '')
    session_key = request.session.session_key
    if not session_key or not isinstance(intent_id, str) or not intent_id:
        raise ValueError('Start checkout again from your bag.')
    cart = Cart.objects.select_for_update().get(session_key=session_key)
    existing = Order.objects.filter(payment_intent_id=intent_id).first()
    if existing:
        if existing.checkout_session_key != session_key:
            raise ValueError('This checkout belongs to a different session.')
        if (existing.shipping_address != str(data.get('shipping_address', '')).strip()
                or (existing.is_guest_order() and existing.guest_email != str(data.get('guest_email', '')).strip().lower())):
            raise ValueError('Shipping details changed. Return to your bag and start a new checkout.')
        return existing
    email = str(data.get('guest_email', '')).strip().lower()
    address = str(data.get('shipping_address', '')).strip()
    if not address or len(address) > 2000:
        raise ValueError('Enter a valid shipping address.')
    if not request.user.is_authenticated:
        validate_email(email)
    items = list(cart.items.select_related('product'))
    if not items:
        raise ValueError('Your bag is empty.')
    totals = Counter()
    for item in items:
        totals[item.product_id] += item.quantity
        if not item.product.active or item.size not in item.product.get_sizes_list() or item.quantity < 1:
            raise ValueError('An item is no longer available. Update your bag.')
    for item in items:
        if totals[item.product_id] > item.product.stock:
            raise ValueError('An item exceeds available stock. Update your bag.')
    amount = sum((i.get_total_price() for i in items), Decimal('0'))
    intent = stripe.PaymentIntent.retrieve(intent_id)
    if (intent.metadata.get('session_key') != session_key or intent.amount != int(amount * 100)
            or intent.currency != 'usd' or intent.status not in ('requires_payment_method', 'requires_confirmation', 'requires_action')):
        raise ValueError('Your bag changed. Start checkout again to update the total.')
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(user=request.user)
    else:
        customer = Customer.objects.create(guest_email=email)
    order = Order.objects.create(customer=customer, guest_email=email if not request.user.is_authenticated else '',
        total_amount=amount, shipping_address=address, payment_intent_id=intent_id, checkout_session_key=session_key)
    OrderItem.objects.bulk_create([OrderItem(order=order, product=i.product, size=i.size, quantity=i.quantity, price=i.product.price) for i in items])
    return order


def _notify(order):
    try:
        send_order_confirmation_email(order)
    except Exception:
        logger.exception('Order %s was saved but confirmation email failed', order.pk)


@transaction.atomic
def complete_order(intent):
    order = Order.objects.select_for_update().get(payment_intent_id=intent['id'])
    if (intent['status'] != 'succeeded' or intent['currency'] != 'usd'
            or intent['amount_received'] != int(order.total_amount * 100)):
        raise ValueError('Payment does not match the order.')
    if order.payment_status in ('completed', 'refunded'):
        return order
    items = list(order.items.all())
    totals = Counter()
    for item in items:
        totals[item.product_id] += item.quantity
    products = {p.pk: p for p in Product.objects.select_for_update().filter(pk__in=totals).order_by('pk')}
    available = all(products[pk].stock >= qty for pk, qty in totals.items())
    if available:
        for pk, qty in totals.items():
            products[pk].stock -= qty
            products[pk].save(update_fields=['stock'])
    else:
        # Keep the paid order for staff resolution; never lose a charge or go negative.
        logger.error('Paid order %s needs stock review before fulfillment', order.pk)
    order.payment_status = 'completed'
    order.status = 'processing' if available else 'pending'
    order.stripe_charge_id = intent.get('latest_charge') or ''
    order.save(update_fields=['payment_status', 'status', 'stripe_charge_id', 'updated_at'])
    cart = Cart.objects.select_for_update().filter(session_key=order.checkout_session_key).first()
    if cart:
        for item in items:
            line = cart.items.filter(product_id=item.product_id, size=item.size).first()
            if line:
                if line.quantity <= item.quantity:
                    line.delete()
                else:
                    line.quantity -= item.quantity
                    line.save(update_fields=['quantity'])
    transaction.on_commit(lambda: _notify(order))
    return order
