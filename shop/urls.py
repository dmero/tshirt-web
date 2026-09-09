from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/data/', views.get_cart_data, name='cart_data'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('prepare-payment/', views.prepare_payment, name='prepare_payment'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('guest-order-lookup/', views.guest_order_lookup, name='guest_order_lookup'),
    path('order/<int:order_id>/refund/', views.refund_order, name='refund_order'),
    path('signup/', views.signup, name='signup'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
