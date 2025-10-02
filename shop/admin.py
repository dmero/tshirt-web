from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

# Register your models here.
from .models import Category, Product, Customer, Order, OrderItem, Cart, CartItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'active', 'created_at']
    list_filter = ['active', 'created_at', 'category']
    list_editable = ['price', 'stock', 'active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

def refund_order_action(modeladmin, request, queryset):
    """Admin action to refund selected orders"""
    refunded_count = 0
    
    for order in queryset:
        if order.payment_status == 'completed':
            # Redirect to refund view for processing
            return redirect(reverse('shop:refund_order', args=[order.id]))
        elif order.payment_status == 'refunded':
            messages.warning(request, f'Order #{order.id} is already refunded.')
        else:
            messages.error(request, f'Order #{order.id} cannot be refunded (status: {order.get_payment_status_display()}).')
    
    if refunded_count > 0:
        messages.success(request, f'{refunded_count} order(s) refunded successfully.')

refund_order_action.short_description = "Process Refund for Selected Order"


def mark_as_shipped(modeladmin, request, queryset):
    """Admin action to mark orders as shipped"""
    updated = 0
    for order in queryset:
        if order.status in ['pending', 'processing']:
            order.status = 'shipped'
            order.save()
            updated += 1
        else:
            messages.warning(request, f'Order #{order.id} cannot be marked as shipped (current status: {order.get_status_display()}).')
    
    if updated > 0:
        messages.success(request, f'{updated} order(s) marked as shipped. Customers will receive email notifications.')

mark_as_shipped.short_description = "Mark as Shipped (Send Email)"


def mark_as_delivered(modeladmin, request, queryset):
    """Admin action to mark orders as delivered"""
    updated = 0
    for order in queryset:
        if order.status == 'shipped':
            order.status = 'delivered'
            order.save()
            updated += 1
        else:
            messages.warning(request, f'Order #{order.id} cannot be marked as delivered (current status: {order.get_status_display()}).')
    
    if updated > 0:
        messages.success(request, f'{updated} order(s) marked as delivered. Customers will receive email notifications.')

mark_as_delivered.short_description = "Mark as Delivered (Send Email)"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'status', 'payment_status', 'tracking_number', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    readonly_fields = ['payment_intent_id', 'stripe_charge_id', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    actions = [mark_as_shipped, mark_as_delivered, refund_order_action]
    search_fields = ['id', 'customer__user__username', 'customer__user__email', 'tracking_number']
    
    def customer_name(self, obj):
        """Display customer username in the list"""
        return obj.customer.user.username
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__user__username'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'status', 'total_amount', 'shipping_address')
        }),
        ('Shipping Details', {
            'fields': ('tracking_number', 'tracking_url'),
            'description': 'Add tracking information when marking order as shipped'
        }),
        ('Payment Details', {
            'fields': ('payment_status', 'payment_method', 'payment_intent_id', 'stripe_charge_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

class CustomerOrderInline(admin.TabularInline):
    """Show all orders for this customer"""
    model = Order
    extra = 0
    can_delete = False
    fields = ['id', 'status', 'payment_status', 'total_amount', 'created_at']
    readonly_fields = ['id', 'status', 'payment_status', 'total_amount', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'created_at']
    inlines = [CustomerOrderInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'postal_code', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']

class CartItemInline(admin.TabularInline):
    model = CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'created_at', 'get_total_items']
    inlines = [CartItemInline]
