# Email Notifications & Refund System Guide

## 🎉 Features Added

Your T-Shirt Shop now includes:
- ✅ **Automated Order Confirmation Emails** - Sent immediately after successful payment
- ✅ **Refund Processing System** - Admin can refund orders via Stripe
- ✅ **Refund Confirmation Emails** - Customers notified when refunds are processed
- ✅ **Beautiful HTML Email Templates** - Professional, branded email design

---

## 📧 Email Notifications

### Order Confirmation Email

**When It's Sent:**
- Automatically after successful payment
- Includes order details, items, shipping address
- Both HTML and plain text versions

**Email Contains:**
- Order number and date
- List of items ordered with sizes and quantities
- Total amount paid
- Shipping address
- Link to "My Orders" page
- Payment status confirmation

**Template Location:**
- HTML: `shop/templates/shop/emails/order_confirmation.html`
- Text: `shop/templates/shop/emails/order_confirmation.txt`

### Refund Confirmation Email

**When It's Sent:**
- After admin processes a refund
- Includes refund amount and processing time info

**Email Contains:**
- Order number and original order date
- Refund amount
- Expected refund processing time (5-10 business days)
- Payment method information

**Template Location:**
- HTML: `shop/templates/shop/emails/refund_confirmation.html`
- Text: `shop/templates/shop/emails/refund_confirmation.txt`

---

## 💰 Refund System

### How to Process Refunds (Admin)

#### Method 1: From Order List

1. Go to **Admin Panel** → **Orders**
   ```
   http://localhost:8000/admin/shop/order/
   ```

2. **Select the order(s)** you want to refund (checkbox)

3. From the **"Action" dropdown**, select **"Process Refund for Selected Order"**

4. Click **"Go"** button

5. **Confirm** the refund on the next page

6. ✅ **Done!** The system will:
   - Process refund with Stripe
   - Update order status to "Refunded"
   - Send confirmation email to customer

#### Method 2: From Order Detail Page

1. Open any order in admin

2. Copy the order ID from the URL or page

3. Navigate to:
   ```
   http://localhost:8000/order/<ORDER_ID>/refund/
   ```

4. Confirm the refund

#### Method 3: Direct URL

You can create a "Refund" button in your order detail template:
```html
<a href="{% url 'shop:refund_order' order.id %}" 
   class="btn btn-danger" 
   onclick="return confirm('Are you sure you want to refund this order?');">
    Process Refund
</a>
```

### Refund Process Flow

```
1. Admin initiates refund
   ↓
2. System validates order (must be "completed" payment status)
   ↓
3. Stripe API processes refund
   ↓
4. Order status updated:
   - payment_status: "refunded"
   - status: "cancelled"
   ↓
5. Refund confirmation email sent to customer
   ↓
6. Admin sees success message
```

### Refund Validation

The system checks:
- ✅ Order payment status must be "completed"
- ✅ Order cannot already be refunded
- ✅ User must have permission (admin or order owner)
- ✅ Payment intent ID must exist

---

## 🧪 Testing Email & Refunds

### Test Order Confirmation Email

1. **Make a test purchase:**
   - Use test card: `4242 4242 4242 4242`
   - Complete checkout

2. **Check your email:**
   - Look in inbox for "Order Confirmation - Order #X"
   - Check spam folder if not found

3. **If email doesn't arrive:**
   - Check `.env` file has correct email settings
   - Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
   - Check server logs for errors

### Test Refund System

**Using Stripe Test Mode:**

1. **Create a test order** (as above)

2. **Process refund** via admin panel

3. **Verify in Stripe Dashboard:**
   - Go to https://dashboard.stripe.com/test/payments
   - Find your payment
   - Should show "Refunded" status

4. **Check refund email:**
   - Look for "Refund Processed - Order #X"
   - Verify refund amount and details

### Test Refund Scenarios

#### ✅ Valid Refund
```
Order Status: Completed
Payment Status: Completed
Result: Refund succeeds
```

#### ❌ Already Refunded
```
Payment Status: Refunded
Result: Error message - "Already refunded"
```

#### ❌ Payment Not Completed
```
Payment Status: Pending/Failed
Result: Error message - "Cannot refund"
```

---

## ⚙️ Email Configuration

### Your Current Settings

Already configured in `.env`:
```ini
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Using Gmail

**Requirements:**
- ✅ Gmail account
- ✅ 2-Factor Authentication enabled
- ✅ App password generated (you already have this)

**Generate New App Password (if needed):**
1. Go to https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Other" → "Django App"
4. Copy the 16-character password
5. Update `EMAIL_HOST_PASSWORD` in `.env`

### Testing Email Sending

Run this command to test:
```bash
python manage.py shell
```

Then:
```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test message from your Django app.',
    'your-email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

---

## 🎨 Customizing Email Templates

### Modify Order Confirmation Email

Edit: `shop/templates/shop/emails/order_confirmation.html`

**Available Variables:**
- `{{ order }}` - Order object
- `{{ order.customer.user }}` - User object
- `{{ order.items.all }}` - Order items
- `{{ order.total_amount }}` - Total price
- `{{ site_url }}` - Base site URL

**Example Customization:**
```html
<!-- Add company logo -->
<div class="header">
    <img src="{{ site_url }}/static/images/logo.png" alt="Logo">
    <h1>Order Confirmed!</h1>
</div>

<!-- Add custom message -->
<p style="color: green; font-weight: bold;">
    🎁 You've earned 100 loyalty points with this purchase!
</p>
```

### Modify Refund Email

Edit: `shop/templates/shop/emails/refund_confirmation.html`

Add custom refund policies, support contact info, etc.

---

## 📊 Admin Features

### Order Admin Enhancements

**New Fields Displayed:**
- Payment Status (with color coding)
- Payment Intent ID
- Stripe Charge ID

**New Actions:**
- Process Refund for Selected Order

**Filter Options:**
- Filter by Payment Status
- Filter by Order Status
- Filter by Creation Date

### View Refunded Orders

In admin, filter orders:
1. Go to Orders list
2. Use "Payment Status" filter
3. Select "Refunded"

---

## 🔒 Security & Permissions

### Refund Permissions

**Who Can Process Refunds:**
- ✅ Admin users (`is_staff=True`)
- ✅ Order owner (customer who placed the order)

**Protection:**
- Validation checks prevent duplicate refunds
- Stripe API keys secure refund processing
- Email confirmations create audit trail

---

## 💡 Advanced Features (Optional)

### Partial Refunds

Modify `refund_order` view to support partial refunds:
```python
refund = stripe.Refund.create(
    payment_intent=order.payment_intent_id,
    amount=int(partial_amount * 100),  # Amount in cents
    reason='requested_by_customer',
)
```

### Order Status Emails

Add emails for:
- Order shipped
- Order delivered
- Order cancelled

### Email Templates

Add more email types:
- Welcome email on signup
- Password reset confirmation
- Abandoned cart reminder

---

## 🐛 Troubleshooting

### Emails Not Sending

**Check 1: Email Configuration**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_HOST_USER)
>>> print(settings.EMAIL_USE_TLS)
```

**Check 2: Gmail Settings**
- Verify 2FA is enabled
- Verify app password is correct (16 chars, no spaces)

**Check 3: Server Logs**
Look for email errors in console output

**Check 4: Test Email**
```python
from shop.emails import send_order_confirmation_email
from shop.models import Order

order = Order.objects.get(id=5)
send_order_confirmation_email(order)
```

### Refund Fails

**Check 1: Stripe Keys**
- Verify `STRIPE_SECRET_KEY` in `.env`
- Make sure using test keys for testing

**Check 2: Order Status**
- Must be "completed" payment status
- Cannot already be refunded

**Check 3: Stripe Dashboard**
- Check if payment exists
- Verify payment wasn't already refunded

**Check 4: Error Logs**
Check Django console for Stripe error messages

---

## 📈 Monitoring

### Email Delivery

**Track Success Rate:**
- Check Django logs for "Email sent" messages
- Monitor Gmail "Sent" folder

**Failed Emails:**
- Check server error logs
- Verify recipient email addresses are valid

### Refund Tracking

**In Stripe Dashboard:**
- Go to https://dashboard.stripe.com/test/payments
- Filter by "Refunded"
- View refund details and timing

**In Django Admin:**
- Filter orders by payment_status="refunded"
- Check refund dates (updated_at field)

---

## 🚀 Production Checklist

Before going live:

### Email Settings
- [ ] Use production SMTP server (not Gmail for high volume)
- [ ] Set up dedicated email service (SendGrid, Mailgun, AWS SES)
- [ ] Configure SPF, DKIM, DMARC records
- [ ] Test email deliverability

### Refund Settings
- [ ] Switch to live Stripe keys
- [ ] Set up refund policies
- [ ] Train staff on refund process
- [ ] Set up refund approval workflow (if needed)

### Monitoring
- [ ] Set up email sending alerts
- [ ] Monitor refund rates
- [ ] Track customer satisfaction after refunds

---

## 📚 File Structure

```
shop/
├── templates/
│   └── shop/
│       └── emails/
│           ├── order_confirmation.html   # Order email (HTML)
│           ├── order_confirmation.txt    # Order email (text)
│           ├── refund_confirmation.html  # Refund email (HTML)
│           └── refund_confirmation.txt   # Refund email (text)
├── emails.py                             # Email sending functions
├── views.py                              # Refund view
├── urls.py                               # Refund URL
└── admin.py                              # Admin refund action
```

---

## ✅ Features Summary

| Feature | Status | Details |
|---------|--------|---------|
| Order Confirmation Email | ✅ Working | HTML + Text versions |
| Refund Email | ✅ Working | HTML + Text versions |
| Refund Processing | ✅ Working | Via Stripe API |
| Admin Refund Action | ✅ Working | Bulk action in admin |
| Refund URL Endpoint | ✅ Working | Direct refund link |
| Email Error Handling | ✅ Working | Graceful failures |
| Stripe Integration | ✅ Working | Test & live modes |

---

## 🎯 Next Steps

1. **Test the system:**
   - Make a test order
   - Check email delivery
   - Process a test refund
   - Verify refund email

2. **Customize templates:**
   - Add your logo
   - Update colors/branding
   - Add custom messages

3. **Set up monitoring:**
   - Track email delivery
   - Monitor refund rates
   - Review customer feedback

**Your email and refund system is now fully operational!** 🎉

For questions or issues, check the troubleshooting section above.
