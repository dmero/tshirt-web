from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.core import mail
import stripe
from .models import Category, Product, CartItem, Customer, Order, OrderItem
from .payments import complete_order
from .emails import send_order_confirmation_email


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('reset-test', email='reset@example.com', password='Original-test-password-937!')

    def test_invalid_email_displays_error(self):
        response = self.client.post('/accounts/password_reset/', {'email': 'invalid'})
        self.assertContains(response, 'Enter a valid email address.')
        self.assertContains(response, 'aria-invalid="true"')

    def test_unknown_email_has_same_confirmation(self):
        response = self.client.post('/accounts/password_reset/', {'email': 'unknown@example.com'}, follow=True)
        self.assertContains(response, 'If an account matches')
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_link_offers_recovery_without_password_fields(self):
        response = self.client.get('/accounts/reset/invalid/invalid/')
        self.assertContains(response, 'Request a new reset link')
        self.assertNotContains(response, 'name="new_password1"')

    def test_reset_validation_completion_and_single_use(self):
        import re
        self.client.post('/accounts/password_reset/', {'email': self.user.email})
        self.assertEqual(len(mail.outbox), 1)
        link = re.search(r'http://testserver(/accounts/reset/\S+)', mail.outbox[0].body).group(1)
        response = self.client.get(link, follow=True)
        self.assertContains(response, 'A fresh start.')
        target = response.redirect_chain[-1][0]
        response = self.client.post(target, {'new_password1': 'Different-new-password-582!', 'new_password2': 'Mismatch-password-583!'})
        self.assertTrue(response.context['form'].errors)
        self.assertContains(response, 'errorlist')
        response = self.client.post(target, {'new_password1': 'Different-new-password-582!', 'new_password2': 'Different-new-password-582!'}, follow=True)
        self.assertContains(response, "You're all set.")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Different-new-password-582!'))
        self.assertContains(self.client.get(link, follow=True), 'Request a new reset link')


class StoreTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Casual', slug='casual')
        self.product = Product.objects.create(name='Cotton Tee', slug='cotton', description='Soft everyday tee', price=Decimal('25'), category=self.category, stock=5, available_sizes='S,M')

    def post(self, path, data):
        return self.client.post(path, data=data, content_type='application/json')

    def add(self, quantity=1, size='M'):
        return self.post('/cart/add/', {'product_id': self.product.pk, 'size': size, 'quantity': quantity})

    def test_catalog_search_category_sort_and_empty_state(self):
        Product.objects.create(name='Budget Tee', slug='budget', description='Basic', price=10, category=self.category, stock=2)
        response = self.client.get('/?q=cotton&category=casual')
        self.assertContains(response, 'Cotton Tee')
        self.assertNotContains(response, 'Budget Tee')
        self.assertContains(self.client.get('/?q=missing'), 'No tees found')
        page = self.client.get('/?sort=price_asc').context['products']
        self.assertEqual(page[0].name, 'Budget Tee')

    def test_catalog_pagination(self):
        for n in range(13):
            Product.objects.create(name=f'Tee {n}', slug=f'tee-{n}', price=20, category=self.category)
        page = self.client.get('/?page=2').context['products']
        self.assertEqual(len(page), 2)

    def test_invalid_cart_inputs_do_not_create_lines(self):
        for quantity, size in [(0,'M'),(-1,'M'),(6,'M'),(1,'XXXL'),('bad','M')]:
            with self.subTest(quantity=quantity, size=size):
                self.assertFalse(self.add(quantity, size).json()['success'])
        self.assertFalse(CartItem.objects.exists())

    def test_stock_is_aggregated_across_sizes(self):
        self.assertTrue(self.add(3, 'S').json()['success'])
        self.assertFalse(self.add(3, 'M').json()['success'])
        self.assertTrue(self.add(2, 'M').json()['success'])
        line = CartItem.objects.get(size='M')
        self.assertFalse(self.post('/cart/update/', {'item_id': line.pk, 'quantity': 3}).json()['success'])

    def test_cart_isolation(self):
        self.add()
        line = CartItem.objects.get()
        other = Client().post('/cart/remove/', {'item_id': line.pk}, content_type='application/json')
        self.assertFalse(other.json()['success'])
        self.assertTrue(CartItem.objects.filter(pk=line.pk).exists())

    def test_mutations_require_post(self):
        for path in ('/cart/add/', '/cart/update/', '/cart/remove/', '/prepare-payment/', '/process-payment/'):
            self.assertEqual(self.client.get(path).status_code, 405)

    def test_csrf_is_required(self):
        response = Client(enforce_csrf_checks=True).post('/cart/add/', {}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_missing_payment_keys_preserve_cart(self):
        self.add()
        self.assertRedirects(self.client.get('/checkout/'), '/cart/')
        self.assertEqual(CartItem.objects.get().quantity, 1)

    @override_settings(STRIPE_PUBLIC_KEY='pk_test_example', STRIPE_SECRET_KEY='sk_test_example')
    def test_checkout_renders_preparation_step(self):
        self.add()
        intent=self.intent(client_secret='pi_test_secret_example')
        with patch('stripe.PaymentIntent.create', return_value=intent):
            response=self.client.get('/checkout/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/prepare-payment/')
        self.assertContains(response, "payment_intent_id: 'pi_test'")

    def intent(self, **kwargs):
        payload = dict(id='pi_test', amount=2500, amount_received=2500, currency='usd', status='requires_payment_method', metadata={'session_key':self.client.session.session_key}, latest_charge='ch_test')
        payload.update(kwargs)
        return stripe.StripeObject.construct_from(payload, 'test')

    def prepare(self, intent=None):
        with patch('stripe.PaymentIntent.retrieve', return_value=intent or self.intent()):
            return self.post('/prepare-payment/', {'payment_intent_id':'pi_test','shipping_address':'123 Test Street, Example, NY 10001','guest_email':'guest@example.com'})

    def test_prepare_rejects_wrong_amount_currency_or_session(self):
        self.add()
        for overrides in ({'amount':1}, {'currency':'eur'}, {'metadata':{'session_key':'different'}}):
            with self.subTest(overrides=overrides):
                self.assertEqual(self.prepare(self.intent(**overrides)).status_code, 400)
        self.assertFalse(Order.objects.exists())

    def test_order_saved_before_charge_and_prepare_is_idempotent(self):
        self.add()
        self.assertTrue(self.prepare().json()['success'])
        self.assertTrue(self.prepare().json()['success'])
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get().payment_status, 'pending')
        self.assertEqual(OrderItem.objects.get().price, Decimal('25'))

    def test_payment_completion_is_idempotent_and_snapshots_price(self):
        self.add()
        self.prepare()
        self.product.price=40
        self.product.save()
        intent = self.intent(status='succeeded')
        with self.captureOnCommitCallbacks(execute=True):
            complete_order(intent)
            complete_order(intent)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)
        self.assertEqual(Order.objects.get().total_amount, Decimal('25'))
        self.assertFalse(CartItem.objects.exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_prepared_shipping_cannot_silently_change_on_retry(self):
        self.add()
        self.prepare()
        response=self.post('/prepare-payment/', {'payment_intent_id':'pi_test','shipping_address':'Changed address','guest_email':'guest@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'start a new checkout', status_code=400)

    def test_short_stock_keeps_paid_order_for_review(self):
        self.add()
        self.prepare()
        Product.objects.filter(pk=self.product.pk).update(stock=0)
        order = complete_order(self.intent(status='succeeded'))
        self.assertEqual((order.payment_status, order.status), ('completed','pending'))
        self.assertEqual(Product.objects.get().stock, 0)

    def test_completion_rejects_underpayment(self):
        self.add()
        self.prepare()
        with self.assertRaises(ValueError):
            complete_order(self.intent(status='succeeded', amount_received=1))
        self.assertEqual(Order.objects.get().payment_status, 'pending')

    def test_webhook_finishes_without_browser_and_preserves_shipped_state(self):
        self.add()
        self.prepare()
        event = {'type':'payment_intent.succeeded','data':{'object':self.intent(status='succeeded')}}
        with patch('stripe.Webhook.construct_event', return_value=event):
            self.assertEqual(self.client.post('/webhook/stripe/', '{}', content_type='application/json').status_code, 200)
            Order.objects.update(status='shipped')
            self.client.post('/webhook/stripe/', '{}', content_type='application/json')
        self.assertEqual(Order.objects.get().status, 'shipped')

    def test_unsigned_webhook_rejected(self):
        self.assertEqual(self.client.post('/webhook/stripe/', '{}', content_type='application/json').status_code, 400)

    def test_foreign_session_cannot_confirm_payment(self):
        self.add()
        self.prepare()
        response=Client().post('/process-payment/', {'payment_intent_id':'pi_test'}, content_type='application/json')
        self.assertFalse(response.json()['success'])

    def test_guest_order_requires_token(self):
        customer=Customer.objects.create(guest_email='guest@example.com')
        order=Order.objects.create(customer=customer,total_amount=25,shipping_address='Example')
        Order.objects.filter(pk=order.pk).update(order_lookup_token=None)
        self.assertEqual(self.client.get(f'/order-success/{order.pk}/').status_code, 302)

    @override_settings(SITE_URL='https://shop.example.com')
    def test_guest_confirmation_email(self):
        self.add()
        self.prepare()
        self.assertTrue(send_order_confirmation_email(Order.objects.get()))
        self.assertEqual(mail.outbox[0].to, ['guest@example.com'])

    def test_refund_get_never_calls_stripe(self):
        user=User.objects.create_user('test-owner', password='local-test-only')
        customer=Customer.objects.create(user=user)
        order=Order.objects.create(customer=customer,total_amount=25,shipping_address='Example',payment_status='completed',payment_intent_id='pi_refund')
        self.client.force_login(user)
        with patch('stripe.Refund.create') as refund:
            self.assertEqual(self.client.get(f'/order/{order.pk}/refund/').status_code, 200)
            refund.assert_not_called()
