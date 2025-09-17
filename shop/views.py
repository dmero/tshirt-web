#from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
import json

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Customer
from .forms import SignUpForm

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
    
    if request.method == 'POST':
        # Create customer if doesn't exist
        customer, created = Customer.objects.get_or_create(user=request.user)
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            total_amount=cart.get_total_price(),
            shipping_address=request.POST.get('shipping_address', ''),
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
        
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('shop:order_success', order_id=order.id)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/checkout.html', context)

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})

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
