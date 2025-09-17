from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Product, Customer, Order, OrderItem
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create a test order for the current user (for testing My Orders page)'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to create order for', default='admin')
        parser.add_argument('--status', type=str, help='Order status', default='pending')
    
    def handle(self, *args, **options):
        username = options['username']
        status = options['status']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return
        
        # Get or create customer
        customer, created = Customer.objects.get_or_create(user=user)
        if created:
            self.stdout.write(f'Created customer for {user.username}')
        
        # Get a sample product
        try:
            product = Product.objects.filter(active=True).first()
            if not product:
                self.stdout.write(self.style.ERROR('No active products found. Run createsampledata first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting product: {e}'))
            return
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            total_amount=Decimal(str(product.price)),
            status=status,
            shipping_address="123 Test Street\nTest City, TC 12345\nUnited States"
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            size='M',
            quantity=1,
            price=product.price
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created test order #{order.id} for {user.username} with status "{status}"'
            )
        )
        self.stdout.write(f'Order total: ${order.total_amount}')
        self.stdout.write(f'Product: {product.name}')
        self.stdout.write('\nYou can now view this order in "My Orders" page.')