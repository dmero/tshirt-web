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
    products = Product.objects.filter(active=True)[:12]
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
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

def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            size = data.get('size')
            quantity = int(data.get('quantity', 1))
            
            product = get_object_or_404(Product, id=product_id, active=True)
            cart = get_cart(request)
            
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
                'message': str(e)
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

def update_cart_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity'))
            
            cart = get_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
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
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

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
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def checkout(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart')
    
    # Create customer if doesn't exist
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    # Calculate total in cents for Stripe
    total_amount = cart.get_total_price()
    total_cents = int(total_amount * 100)
    
    # Create Stripe PaymentIntent
    try:
        # Validate amount
        if total_cents <= 0:
            messages.error(request, 'Invalid cart total. Please check your cart.')
            return redirect('shop:cart')
        
        intent = stripe.PaymentIntent.create(
            amount=total_cents,
            currency='usd',
            metadata={
                'user_id': request.user.id,
                'customer_id': customer.id,
            }
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        messages.error(request, f'Payment system error: {str(e)}')
        return redirect('shop:cart')
    except Exception as e:
        logger.error(f"Unexpected error in checkout: {str(e)}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('shop:cart')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret,
        'total_amount': total_amount,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def process_payment(request):
    """Handle payment confirmation and create order"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get('payment_intent_id')
            shipping_address = data.get('shipping_address', '')
            
            # Verify payment intent with Stripe
            try:
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            except stripe.error.StripeError as e:
                logger.error(f"Stripe retrieve error: {str(e)}")
                return JsonResponse({'success': False, 'message': 'Payment verification failed'})
            
            if intent.status != 'succeeded':
                return JsonResponse({'success': False, 'message': 'Payment not completed'})
            
            # Get cart and customer
            cart = get_cart(request)
            cart_items = cart.items.all()
            customer, created = Customer.objects.get_or_create(user=request.user)
            
            # Get charge ID safely
            charge_id = ''
            if hasattr(intent, 'charges') and intent.charges:
                charges_data = intent.charges.get('data', [])
                if charges_data and len(charges_data) > 0:
                    charge_id = charges_data[0].get('id', '')
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=cart.get_total_price(),
                shipping_address=shipping_address,
                payment_status='completed',
                payment_intent_id=payment_intent_id,
                stripe_charge_id=charge_id,
                status='processing'
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    size=cart_item.size,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )
            
            # Clear cart
            cart_items.delete()
            
            # Send order confirmation email
            try:
                send_order_confirmation_email(order, request)
            except Exception as e:
                logger.error(f"Failed to send order confirmation email: {str(e)}")
                # Don't fail the order if email fails
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'message': f'Order #{order.id} placed successfully!'
            })
            
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
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
    
    # Check if already refunded
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
                )
                logger.info(f"Stripe refund created: {refund.id} for order #{order.id}")
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
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"PaymentIntent succeeded: {payment_intent['id']}")
        
        # Update order status if it exists
        try:
            order = Order.objects.get(payment_intent_id=payment_intent['id'])
            order.payment_status = 'completed'
            order.status = 'processing'
            order.save()
        except Order.DoesNotExist:
            logger.warning(f"Order not found for payment_intent: {payment_intent['id']}")
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        logger.warning(f"PaymentIntent failed: {payment_intent['id']}")
        
        # Update order status if it exists
        try:
            order = Order.objects.get(payment_intent_id=payment_intent['id'])
            order.payment_status = 'failed'
            order.save()
        except Order.DoesNotExist:
            pass
    
    return HttpResponse(status=200)
