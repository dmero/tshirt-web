# Stripe Payment Integration Setup Guide

## 🎉 Integration Complete!

Credit card payment processing using **Stripe** has been successfully integrated into your T-Shirt Shop.

---

## 📋 What Was Added

### 1. **Database Changes**
- Added payment tracking fields to `Order` model:
  - `payment_status` - Track payment state (pending/completed/failed/refunded)
  - `payment_intent_id` - Stripe PaymentIntent ID
  - `stripe_charge_id` - Stripe Charge ID for refunds
  - `payment_method` - Payment method used (card/other)

### 2. **New Views**
- `checkout()` - Creates Stripe PaymentIntent and displays payment form
- `process_payment()` - Processes successful payments and creates orders
- `stripe_webhook()` - Handles Stripe webhook events for payment confirmations

### 3. **Updated Templates**
- `checkout.html` - Now includes Stripe Elements for secure card input

### 4. **New Dependencies**
- `stripe==7.0.0` - Official Stripe Python library

---

## 🚀 Setup Instructions

### Step 1: Install Stripe Package

```bash
# Activate your environment
conda activate tshirt

# Install the Stripe package
pip install stripe==7.0.0
```

### Step 2: Get Stripe API Keys

1. **Create a Stripe Account:**
   - Go to https://dashboard.stripe.com/register
   - Sign up for a free account

2. **Get Your Test API Keys:**
   - Navigate to https://dashboard.stripe.com/test/apikeys
   - Copy your **Publishable key** (starts with `pk_test_`)
   - Copy your **Secret key** (starts with `sk_test_`)

### Step 3: Add Stripe Keys to .env

Add these lines to your `.env` file:

```ini
# Stripe Payment Configuration
STRIPE_PUBLIC_KEY=pk_test_your_actual_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
STRIPE_WEBHOOK_SECRET=  # Leave empty for now, will be set up later
```

### Step 4: Run Database Migrations

```bash
# Stop the server (Ctrl+C)

# Create migrations for the new payment fields
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Restart the server
python manage.py runserver 0.0.0.0:8000
```

---

## 🧪 Testing Payments

Stripe provides test card numbers that simulate different scenarios:

### Successful Payment
- **Card Number:** `4242 4242 4242 4242`
- **Expiry:** Any future date (e.g., `12/34`)
- **CVC:** Any 3 digits (e.g., `123`)
- **ZIP:** Any 5 digits (e.g., `12345`)

### Other Test Cards
- **Declined:** `4000 0000 0000 0002`
- **Insufficient Funds:** `4000 0000 0000 9995`
- **Requires Authentication (3D Secure):** `4000 0025 0000 3155`

See full list: https://stripe.com/docs/testing

---

## 💳 How It Works

### Payment Flow

1. **User adds items to cart** and proceeds to checkout
2. **Django creates a PaymentIntent** with Stripe (amount reserved but not charged)
3. **User enters card details** into Stripe Elements (secure, PCI-compliant form)
4. **Stripe processes the payment** and confirms success
5. **Django creates the order** with payment confirmation
6. **Cart is cleared** and user sees success page

### Security Features
- ✅ Card details never touch your server (Stripe Elements handles it)
- ✅ PCI DSS compliant out of the box
- ✅ 3D Secure authentication support
- ✅ Webhook verification for payment confirmations

---

## 🔗 Setting Up Webhooks (Optional but Recommended)

Webhooks allow Stripe to notify your app about payment events.

### Development (Using Stripe CLI)

1. **Install Stripe CLI:**
   - Download from https://stripe.com/docs/stripe-cli
   
2. **Login to Stripe:**
   ```bash
   stripe login
   ```

3. **Forward webhooks to local server:**
   ```bash
   stripe listen --forward-to localhost:8000/webhook/stripe/
   ```
   
4. **Copy the webhook signing secret** (starts with `whsec_`) to your `.env`:
   ```ini
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

### Production Webhooks

1. **Go to Stripe Dashboard:**
   - https://dashboard.stripe.com/webhooks

2. **Add endpoint:**
   - URL: `https://yourdomain.com/webhook/stripe/`
   - Events to send: `payment_intent.succeeded`, `payment_intent.payment_failed`

3. **Copy signing secret** to your production `.env`

---

## 📊 Admin Interface

The Order admin now shows payment information:
- Payment Status (Pending/Completed/Failed/Refunded)
- Payment Intent ID
- Stripe Charge ID

Access at: http://localhost:8000/admin/shop/order/

---

## 🛠️ Customization

### Change Currency

In `shop/views.py` (line 190):
```python
intent = stripe.PaymentIntent.create(
    amount=total_cents,
    currency='usd',  # Change to 'eur', 'gbp', etc.
    ...
)
```

### Add Customer Billing Info

Extend the `Customer` model to store billing address and pass it to Stripe.

### Add Order Confirmation Emails

In `process_payment()` view, after order creation:
```python
from django.core.mail import send_mail

send_mail(
    f'Order Confirmation #{order.id}',
    f'Thank you for your order! Total: ${order.total_amount}',
    settings.DEFAULT_FROM_EMAIL,
    [request.user.email],
)
```

---

## 🐛 Troubleshooting

### "Stripe is not defined" error
- Make sure Stripe.js is loaded: Check browser console
- Verify STRIPE_PUBLIC_KEY is set in .env

### "No such payment_intent" error
- Check that STRIPE_SECRET_KEY is correct
- Verify you're using the right test/live keys

### Webhook signature verification fails
- Make sure STRIPE_WEBHOOK_SECRET matches the endpoint secret
- Check that raw request body is passed to webhook handler

### Payment succeeds but order not created
- Check Django logs for errors
- Verify database connection is working
- Check `process_payment` view logs

---

## 📚 Resources

- **Stripe Documentation:** https://stripe.com/docs
- **Stripe API Reference:** https://stripe.com/docs/api
- **Stripe Testing:** https://stripe.com/docs/testing
- **Stripe Dashboard:** https://dashboard.stripe.com

---

## ✅ Next Steps

1. Install Stripe: `pip install stripe`
2. Get API keys from Stripe Dashboard
3. Add keys to `.env` file
4. Run migrations: `python manage.py makemigrations && python manage.py migrate`
5. Test checkout with test card: `4242 4242 4242 4242`
6. Set up webhooks (optional but recommended)

**Your store is now ready to accept real credit card payments! 🎉**

For production deployment:
- Switch to live API keys (not test keys)
- Enable webhook endpoints
- Consider adding fraud detection rules in Stripe Dashboard
- Set up automatic payout schedules
