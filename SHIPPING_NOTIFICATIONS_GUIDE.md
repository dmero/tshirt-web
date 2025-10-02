# Shipped & Delivered Email Notifications Guide

## 🎉 New Feature Added!

Your T-Shirt Shop now **automatically sends email notifications** when orders are shipped or delivered!

---

## 📧 What's Included

### **1. Shipped Notification Email** 📦
- **Sent When:** Order status changes to "Shipped"
- **Includes:**
  - Tracking number (if provided)
  - Tracking URL link
  - Order details and items
  - Expected delivery time (3-5 days)
  - Shipping address

### **2. Delivered Notification Email** ✅
- **Sent When:** Order status changes to "Delivered"
- **Includes:**
  - Delivery confirmation
  - Order details
  - Request for feedback/review
  - Customer support information

---

## 🚀 How It Works

### **Automatic Email Sending**

The system uses **Django Signals** to automatically detect when an order status changes:

```
Order Status Change → Signal Triggered → Email Sent Automatically
```

**No manual work required!** Just update the order status in admin, and customers get notified instantly.

---

## 🎯 How to Use (Admin)

### **Method 1: Bulk Actions (Recommended)**

#### **Mark Orders as Shipped:**

1. **Go to Admin Panel** → **Orders**
   ```
   http://localhost:8000/admin/shop/order/
   ```

2. **Select order(s)** you want to mark as shipped (checkbox)

3. **Action dropdown** → Select **"Mark as Shipped (Send Email)"**

4. **Click "Go"**

5. ✅ **Done!** 
   - Order status → "Shipped"
   - Email sent automatically
   - Customer notified

#### **Mark Orders as Delivered:**

1. **Select shipped order(s)** (checkbox)

2. **Action dropdown** → Select **"Mark as Delivered (Send Email)"**

3. **Click "Go"**

4. ✅ **Done!**
   - Order status → "Delivered"
   - Email sent automatically
   - Customer notified

---

### **Method 2: Edit Individual Order**

#### **To Mark as Shipped:**

1. **Open order** in admin

2. **Add tracking information** (optional but recommended):
   - **Tracking Number:** `1234567890`
   - **Tracking URL:** `https://www.ups.com/track?tracknum=1234567890`

3. **Change Status** dropdown → Select **"Shipped"**

4. **Click "Save"**

5. ✅ **Email sent automatically with tracking info!**

#### **To Mark as Delivered:**

1. **Open shipped order** in admin

2. **Change Status** dropdown → Select **"Delivered"**

3. **Click "Save"**

4. ✅ **Delivery confirmation email sent!**

---

## 📋 Order Workflow

### **Complete Order Lifecycle:**

```
1. Customer Places Order → Order Confirmation Email ✅
   Status: "Processing"
   
2. Admin Marks as Shipped → Shipped Email ✅
   Status: "Shipped"
   (Include tracking number)
   
3. Admin Marks as Delivered → Delivered Email ✅
   Status: "Delivered"
   (Request feedback)
   
4. (Optional) Refund → Refund Email ✅
   Status: "Cancelled"
```

---

## 🧪 Testing Notifications

### **Test Shipped Email:**

1. **Create a test order** (use Stripe test card)

2. **Go to Admin** → **Orders** → Select your order

3. **Add tracking info:**
   - Tracking Number: `TEST123456789`
   - Tracking URL: `https://example.com/track/TEST123456789`

4. **Select Action:** "Mark as Shipped"

5. **Check your email** for "Your Order Has Shipped - Order #X"

### **Test Delivered Email:**

1. **Use the same order** (must be "Shipped" status)

2. **Select Action:** "Mark as Delivered"

3. **Check your email** for "Your Order Has Been Delivered - Order #X"

### **Quick Test via Django Shell:**

```bash
python manage.py shell
```

```python
from shop.models import Order
from shop.emails import send_order_shipped_email, send_order_delivered_email

# Get an order
order = Order.objects.get(id=5)

# Test shipped email
send_order_shipped_email(
    order=order,
    tracking_number="TEST123456",
    tracking_url="https://tracking.com/TEST123456"
)

# Test delivered email
send_order_delivered_email(order=order)

# Check your email!
```

---

## 🎨 Email Templates

### **Shipped Email Design:**
- 🟠 Orange header with package icon
- Tracking number display (large, prominent)
- "Track Package" button
- Expected delivery: 3-5 business days

### **Delivered Email Design:**
- 🟢 Green header with checkmark
- Delivery confirmation message
- Feedback request section
- Customer support links

---

## 📊 Admin Panel Enhancements

### **New Features Added:**

#### **Order List Display:**
- ✅ Tracking number column
- ✅ Search by tracking number
- ✅ Filter by order status

#### **New Admin Actions:**
- ✅ **Mark as Shipped (Send Email)**
- ✅ **Mark as Delivered (Send Email)**
- ✅ Process Refund (existing)

#### **Order Detail Page:**
- ✅ Shipping Details section
- ✅ Tracking number field
- ✅ Tracking URL field
- ✅ Status change tracking

---

## 🔧 Technical Details

### **Files Created:**

| File | Purpose |
|------|---------|
| `shop/signals.py` | Auto-detect status changes |
| `shop/templates/shop/emails/order_shipped.html` | Shipped email (HTML) |
| `shop/templates/shop/emails/order_shipped.txt` | Shipped email (text) |
| `shop/templates/shop/emails/order_delivered.html` | Delivered email (HTML) |
| `shop/templates/shop/emails/order_delivered.txt` | Delivered email (text) |

### **Files Modified:**

| File | Changes |
|------|---------|
| `shop/models.py` | Added tracking_number, tracking_url fields |
| `shop/emails.py` | Added shipped & delivered email functions |
| `shop/admin.py` | Added admin actions & tracking fields |
| `shop/apps.py` | Registered signals |
| `shop/views.py` | Updated imports |

### **Database Changes:**

New fields added to `Order` model:
- `tracking_number` (CharField, optional)
- `tracking_url` (URLField, optional)

**Migration required!** (see below)

---

## 🚀 Setup Instructions

### **Step 1: Create Migrations**

```bash
python manage.py makemigrations
```

Expected output:
```
Migrations for 'shop':
  shop\migrations\0003_order_tracking_number_order_tracking_url.py
    - Add field tracking_number to order
    - Add field tracking_url to order
```

### **Step 2: Apply Migrations**

```bash
python manage.py migrate
```

### **Step 3: Restart Server**

```bash
python manage.py runserver 0.0.0.0:8000
```

### **Step 4: Test!**

1. Make a test order
2. Mark as shipped
3. Check email inbox
4. Mark as delivered
5. Check email again

✅ **Done!**

---

## 🎯 Best Practices

### **When to Mark as Shipped:**

- ✅ When package leaves your facility
- ✅ After receiving tracking number from carrier
- ✅ Include tracking info for customer convenience

### **When to Mark as Delivered:**

- ✅ After carrier confirms delivery
- ✅ When package tracking shows "Delivered"
- ✅ After customer confirms receipt (if applicable)

### **Tracking Numbers:**

**Recommended Format:**
- USPS: `9400 1000 0000 0000 0000 00`
- UPS: `1Z999AA10123456784`
- FedEx: `123456789012`
- DHL: `1234567890`

**Include Tracking URL for:**
- Better customer experience
- Reduce support inquiries
- Build trust and transparency

---

## 📧 Email Customization

### **Modify Shipped Email:**

Edit: `shop/templates/shop/emails/order_shipped.html`

**Add Company Logo:**
```html
<div class="header">
    <img src="{{ site_url }}/static/images/logo.png" alt="Logo" style="max-width: 150px;">
    <h1>📦 Your Order Has Shipped!</h1>
</div>
```

**Change Expected Delivery:**
```html
<p><strong>Expected Delivery:</strong> 2-3 business days</p>
```

**Add Custom Carrier Links:**
```html
{% if 'USPS' in tracking_number %}
    <a href="https://tools.usps.com/go/TrackConfirmAction?tLabels={{ tracking_number }}">
        Track with USPS
    </a>
{% elif 'UPS' in tracking_number %}
    <a href="https://www.ups.com/track?tracknum={{ tracking_number }}">
        Track with UPS
    </a>
{% endif %}
```

### **Modify Delivered Email:**

Edit: `shop/templates/shop/emails/order_delivered.html`

**Add Review Request:**
```html
<div class="highlight-box">
    <h3>⭐ Leave a Review</h3>
    <p>Share your experience and help other customers!</p>
    <a href="{{ site_url }}/product/{{ order.items.first.product.slug }}/#reviews" class="btn">
        Write a Review
    </a>
</div>
```

**Add Discount Code:**
```html
<p>
    <strong>Thank you for your order!</strong><br>
    Enjoy 10% off your next purchase with code: <strong>THANKYOU10</strong>
</p>
```

---

## 🐛 Troubleshooting

### **Emails Not Sending**

**Check 1: Verify Signals Are Loaded**
```bash
python manage.py shell
```
```python
from django.apps import apps
config = apps.get_app_config('shop')
print(config.ready)  # Should not error
```

**Check 2: Check Status Change**
- Emails only send when status **changes**
- If order already "shipped", won't resend email
- Must change from "processing" → "shipped"

**Check 3: Server Logs**
Look for:
```
Order #X status changed to shipped. Sending email...
Order shipped email sent for order #X to user@email.com
```

**Check 4: Email Configuration**
```python
from django.conf import settings
print(settings.EMAIL_HOST_USER)
print(settings.DEFAULT_FROM_EMAIL)
```

### **Tracking Info Not Showing**

- Make sure you **filled in** tracking fields before changing status
- Or add tracking info **then** save order again
- Signals trigger on save, so re-save to send updated email

### **Wrong Email Template**

Clear template cache:
```bash
# Restart server
python manage.py runserver 0.0.0.0:8000
```

---

## 🔒 Security & Permissions

### **Who Can Mark Orders as Shipped/Delivered:**

- ✅ Admin users (`is_staff=True`)
- ✅ Users with order change permissions

### **Email Delivery:**

- Sent to `order.customer.user.email`
- Falls back gracefully if no email address
- Logs warnings for missing emails
- Won't break order processing if email fails

---

## 📈 Monitoring & Analytics

### **Track Email Delivery:**

**In Server Logs:**
```
[INFO] Order shipped email sent for order #5 to customer@email.com
[INFO] Order delivered email sent for order #6 to customer@email.com
```

**In Django Shell:**
```python
from shop.models import Order

# Count shipped orders
Order.objects.filter(status='shipped').count()

# Count delivered orders
Order.objects.filter(status='delivered').count()

# Get recent deliveries
Order.objects.filter(status='delivered').order_by('-updated_at')[:10]
```

### **Customer Satisfaction:**

After implementing:
- Monitor support tickets (should decrease)
- Track "Where is my order?" inquiries
- Measure repeat purchase rate

---

## 🎁 Bonus Features Ideas

### **Future Enhancements:**

1. **SMS Notifications** (using Twilio)
   - Send text when shipped
   - Send text when delivered

2. **Push Notifications** (web push)
   - Real-time tracking updates

3. **Order Tracking Page**
   - Customer-facing tracking page
   - Live updates from carrier API

4. **Auto-Update from Carriers**
   - Integrate with USPS/UPS/FedEx APIs
   - Automatically mark as delivered

5. **Estimated Delivery Date**
   - Calculate based on carrier and location
   - Show in shipped email

---

## ✅ Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Shipped Email | ✅ Working | Auto-sent on status change |
| Delivered Email | ✅ Working | Auto-sent on status change |
| Tracking Number | ✅ Working | Optional field |
| Tracking URL | ✅ Working | Optional field |
| Admin Actions | ✅ Working | Bulk update orders |
| Django Signals | ✅ Working | Auto-detect changes |
| Email Templates | ✅ Working | HTML + Text versions |

---

## 🎯 Quick Reference

### **Admin Actions:**
- **Mark as Shipped** → Changes status + sends email
- **Mark as Delivered** → Changes status + sends email
- **Process Refund** → Refunds payment + sends email

### **Order Status Flow:**
```
Pending → Processing → Shipped → Delivered
                          ↓
                      Cancelled (Refunded)
```

### **Email Timeline:**
1. **Order placed** → Confirmation email
2. **Status → Shipped** → Shipped email (with tracking)
3. **Status → Delivered** → Delivered email (with feedback request)
4. **(Optional) Refunded** → Refund email

---

**Your shipping notification system is now fully operational!** 🎉📦✅

Customers will love staying updated on their orders automatically!
