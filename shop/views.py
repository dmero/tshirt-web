#from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.views.decorators.http import require_POST
import json
import logging
import stripe

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Customer
from .forms import SignUpForm
from .emails import (
    send_order_confirmation_email,
    send_refund_confirmation_email,
    send_order_shipped_email,
    send_order_delivered_email
)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

def index(request):
    products = Product.objects.filter(active=True).select_related('category')
    query = request.GET.get('q', '').strip()[:100]
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'newest')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        products = products.filter(category__slug=category)
    products = products.order_by({'price_asc': 'price', 'price_desc': '-price', 'name': 'name'}.get(sort, '-created_at'), 'pk')
    products = Paginator(products, 12).get_page(request.GET.get('page'))
    categories = Category.objects.all().order_by('name')

    context = {
        'products': products,
        'categories': categories, 'query': query, 'selected_category': category, 'sort': sort,
    }
    return render(request, 'shop/index.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    sizes = product.get_sizes_list()

    context = {
        'product': product,
        'sizes': sizes,
    }
    return render(request, 'shop/product_detail.html', context)

def get_cart(request):
    """Get or create cart for current session"""
    if not request.session.session_key:
        request.session.create()

    cart, created = Cart.objects.get_or_create(
        session_key=request.session.session_key
    )
    return cart

@require_POST
@transaction.atomic
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            size = data.get('size')
            quantity = int(data.get('quantity', 1))

            product = get_object_or_404(Product, id=product_id, active=True)
            cart = get_cart(request)

            Cart.objects.select_for_update().get(pk=cart.pk)
            current = cart.items.filter(product=product).aggregate(n=Sum('quantity'))['n'] or 0
            if size not in product.get_sizes_list() or quantity < 1 or quantity + current > product.stock:
                return JsonResponse({'success': False, 'message': 'Choose an available size and a quantity within stock.'}, status=400)
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                size=size,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({
                'success': True,
                'message': f'{product.name} ({size}) added to cart',
                'cart_total': cart.get_total_items()
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Unable to process this request. Check your input and try again.'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def cart_view(request):
    cart = get_cart(request)
    cart_items = cart.items.all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/cart.html', context)

def get_cart_data(request):
    cart = get_cart(request)
    cart_items = []

    for item in cart.items.all():
        cart_items.append({
            'id': item.id,
            'product_name': item.product.name,
            'product_image': item.product.image.url if item.product.image else '',
            'size': item.size,
            'quantity': item.quantity,
            'price': float(item.product.price),
            'total': float(item.get_total_price()),
        })

    return JsonResponse({
        'items': cart_items,
        'total_items': cart.get_total_items(),
        'total_price': float(cart.get_total_price()),
    })

@require_POST
@transaction.atomic
def update_cart_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity'))

            cart = get_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

            Cart.objects.select_for_update().get(pk=cart.pk)
            other = cart.items.filter(product=cart_item.product).exclude(pk=cart_item.pk).aggregate(n=Sum('quantity'))['n'] or 0
            if quantity < 0 or quantity + other > cart_item.product.stock or not cart_item.product.active:
                return JsonResponse({'success': False, 'message': 'That quantity is not available.'}, status=400)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()

            return JsonResponse({
                'success': True,
                'cart_total': cart.get_total_items(),
                'cart_price': float(cart.get_total_price())
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Unable to process this request. Check your input and try again.'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@require_POST
@transaction.atomic
def remove_from_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')

            cart = get_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.delete()

            return JsonResponse({
                'success': True,
                'cart_total': cart.get_total_items(),
                'cart_price': float(cart.get_total_price())
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Unable to process this request. Check your input and try again.'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def checkout(request):
    cart = get_cart(request)
    cart_items = cart.items.all()

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart')

    if not settings.STRIPE_PUBLIC_KEY or not settings.STRIPE_SECRET_KEY:
        messages.info(request, 'Checkout is not available yet. Your items are saved in your bag.')
        return redirect('shop:cart')
    # Calculate total in cents for Stripe
    total_amount = cart.get_total_price()
    total_cents = int(total_amount * 100)

    # Create Stripe PaymentIntent
    try:
        # Validate amount
        if total_cents <= 0:
            messages.error(request, 'Invalid cart total. Please check your cart.')
            return redirect('shop:cart')

        metadata = {'session_key': request.session.session_key}

        # Add user info if authenticated
        if request.user.is_authenticated:
            customer, created = Customer.objects.get_or_create(user=request.user)
            metadata['user_id'] = request.user.id
            metadata['customer_id'] = customer.id

        intent = stripe.PaymentIntent.create(
            amount=total_cents,
            currency='usd',
            metadata=metadata
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        messages.error(request, 'Payment service is temporarily unavailable. Please try again.')
        return redirect('shop:cart')
    except Exception as e:
        logger.error(f"Unexpected error in checkout: {str(e)}")
        messages.error(request, 'Unable to start checkout. Please try again.')
        return redirect('shop:cart')

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret,
        'payment_intent_id': intent.id,
        'total_amount': total_amount,
        'is_guest': not request.user.is_authenticated,
    }
    return render(request, 'shop/checkout.html', context)

@require_POST
def prepare_payment(request):
    """Persist the immutable order before the browser can confirm payment."""
    from .payments import prepare_order
    try:
        order = prepare_order(request, json.loads(request.body))
        return JsonResponse({'success': True, 'order_id': order.pk})
    except (ValueError, ValidationError) as exc:
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)
    except Exception:
        logger.exception('Unable to prepare checkout')
        return JsonResponse({'success': False, 'message': 'Unable to prepare checkout. Please try again.'}, status=503)


@require_POST
def process_payment(request):
    from .payments import complete_order
    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, payment_intent_id=data.get('payment_intent_id'), checkout_session_key=request.session.session_key or '')
        if not request.session.session_key:
            return JsonResponse({'success': False}, status=403)
        intent = stripe.PaymentIntent.retrieve(order.payment_intent_id)
        order = complete_order(intent)
        return JsonResponse({'success': True, 'order_id': order.pk, 'order_token': order.order_lookup_token, 'is_guest': order.is_guest_order()})
    except Exception:
        logger.exception('Payment confirmation failed')
        return JsonResponse({'success': False, 'message': 'Payment confirmation is pending. Please check your orders before trying again.'}, status=400)


def order_success(request, order_id):
    """Order success page - accessible by authenticated users or via token for guests"""
    order = get_object_or_404(Order, id=order_id)

    # Check access permissions
    if request.user.is_authenticated:
        # Authenticated users can only view their own orders
        if order.customer.user != request.user:
            messages.error(request, 'You do not have permission to view this order.')
            return redirect('shop:index')
    else:
        # Guest users need the correct token in session or URL
        token = request.GET.get('token') or request.session.get(f'order_token_{order_id}')
        if not token or not order.order_lookup_token or token != order.order_lookup_token:
            messages.error(request, 'Invalid order access.')
            return redirect('shop:index')
        # Store token in session for this order
        request.session[f'order_token_{order_id}'] = token

    return render(request, 'shop/order_success.html', {'order': order})


@login_required
def refund_order(request, order_id):
    """
    Process refund for an order (Admin or customer-initiated)
    """
    # Get the order
    order = get_object_or_404(Order, id=order_id)

    # Check if user has permission (admin or order owner)
    if not (request.user.is_staff or order.customer.user == request.user):
        messages.error(request, 'You do not have permission to refund this order.')
        return redirect('shop:my_orders')

    if request.method != 'POST':
        return render(request, 'shop/refund_confirm.html', {'order': order})
    # Check if already refunded
    if not order.payment_intent_id:
        messages.error(request, 'This order has no payment reference. Please contact the shop for assistance.')
        return redirect('shop:my_orders')
    if order.payment_status == 'refunded':
        messages.warning(request, f'Order #{order.id} has already been refunded.')
        return redirect('admin:shop_order_change', order.id) if request.user.is_staff else redirect('shop:my_orders')

    # Check if payment was completed
    if order.payment_status != 'completed':
        messages.error(request, f'Order #{order.id} cannot be refunded. Payment status: {order.get_payment_status_display()}')
        return redirect('admin:shop_order_change', order.id) if request.user.is_staff else redirect('shop:my_orders')

    try:
        # Process refund with Stripe
        if order.payment_intent_id:
            try:
                refund = stripe.Refund.create(
                    payment_intent=order.payment_intent_id,
                    reason='requested_by_customer',
                    idempotency_key=f'order-refund-{order.pk}',
                )
                logger.info(f"Stripe refund created: {refund.id} for order #{order.id}")
                if refund.status != 'succeeded':
                    messages.info(request, 'The refund is pending confirmation. Please check its status before retrying.')
                    return redirect('shop:my_orders')
            except stripe.error.StripeError as e:
                logger.error(f"Stripe refund failed for order #{order.id}: {str(e)}")
                messages.error(request, f'Refund failed: {str(e)}')
                return redirect('admin:shop_order_change', order.id) if request.user.is_staff else redirect('shop:my_orders')

        # Update order status
        order.payment_status = 'refunded'
        order.status = 'cancelled'
        order.save()

        # Send refund confirmation email
        try:
            send_refund_confirmation_email(order, request)
        except Exception as e:
            logger.error(f"Failed to send refund confirmation email: {str(e)}")

        messages.success(request, f'Order #{order.id} has been refunded successfully. The customer will receive a confirmation email.')

    except Exception as e:
        logger.error(f"Refund processing error for order #{order.id}: {str(e)}")
        messages.error(request, f'Error processing refund: {str(e)}')

    # Redirect based on user type
    if request.user.is_staff:
        return redirect('admin:shop_order_change', order.id)
    else:
        return redirect('shop:my_orders')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user is not None:
                login(request, user)
                return redirect('shop:index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def my_orders(request):
    try:
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
    except Customer.DoesNotExist:
        orders = []

    context = {
        'orders': orders,
    }
    return render(request, 'shop/my_orders.html', context)

def guest_order_lookup(request):
    """Allow guests to look up their orders"""
    order = None
    error = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        order_id = request.POST.get('order_id', '').strip()

        if email and order_id:
            try:
                order = Order.objects.get(
                    id=order_id,
                    guest_email=email
                )
                # Store token in session for accessing order details
                request.session[f'order_token_{order.id}'] = order.order_lookup_token
            except Order.DoesNotExist:
                error = "Order not found. Please check your email and order number."
            except ValueError:
                error = "Invalid order number."
        else:
            error = "Please provide both email and order number."

    context = {
        'order': order,
        'error': error,
    }
    return render(request, 'shop/guest_order_lookup.html', context)

class PlainTextPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.txt'

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        logger.error("Invalid webhook payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        logger.error("Invalid webhook signature")
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        from .payments import complete_order
        try:
            complete_order(event['data']['object'])
        except Order.DoesNotExist:
            logger.error('Payment has no saved order; requires reconciliation')
            return HttpResponse(status=500)
        except (ValueError, ValidationError):
            logger.exception('Payment amount or currency mismatch')
            return HttpResponse(status=400)
    return HttpResponse(status=200)
