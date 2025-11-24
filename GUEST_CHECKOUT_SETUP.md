# Guest Checkout Implementation Guide

## Overview
Guest checkout functionality has been successfully implemented for your T-shirt shop. Customers can now purchase items without creating an account, while maintaining the option to create accounts for order tracking and future purchases.

## What Has Been Implemented

### 1. **Model Changes** (`shop/models.py`)
- **Customer Model**:
  - `user` field is now optional (`null=True, blank=True`)
  - Added `guest_email` field for guest customers
  - Added `is_guest()` method to check if customer is guest

- **Order Model**:
  - Added `guest_email` field to store guest customer email
  - Added `order_lookup_token` (UUID) for secure guest order tracking
  - Added `is_guest_order()` method
  - Auto-generates unique lookup token on order creation

### 2. **View Updates** (`shop/views.py`)
- **checkout()**: Removed `@login_required` decorator - now accessible to all users
- **process_payment()**: Handles both authenticated and guest checkouts
  - Validates guest email
  - Creates guest customer records
  - Returns order token for guest access
- **order_success()**: Supports token-based access for guest orders
- **guest_order_lookup()**: New view for guests to track orders using email + order ID

### 3. **URL Routes** (`shop/urls.py`)
- Added: `/guest-order-lookup/` - Guest order tracking page

### 4. **Templates**

#### **checkout.html**
- Conditional email field for guest users
- Collects guest email before payment
- Handles token-based redirect for guest orders

#### **guest_order_lookup.html** (NEW)
- Form to search orders by email + order number
- Displays full order details if found
- Shows order status, items, tracking info

#### **order_success.html**
- Enhanced with guest-specific messaging
- Shows order tracking instructions for guests
- Link to guest order lookup page

#### **base.html**
- Added "Track Order" link in navigation for non-authenticated users

## Database Migration Required

⚠️ **IMPORTANT**: You must run migrations to apply the database changes.

```bash
# Activate your virtual environment first (if you have one)
# Then run:

python manage.py makemigrations
python manage.py migrate
```

Expected migrations:
- `Customer.user` - Change to nullable
- `Customer.guest_email` - New field
- `Order.guest_email` - New field
- `Order.order_lookup_token` - New unique field

## How It Works

### Guest Checkout Flow

1. **Cart**: Guest adds items to cart (session-based, no login required)
2. **Checkout**: Guest clicks "Proceed to Checkout" - no login wall
3. **Contact Info**: Guest enters email address (required for confirmation)
4. **Shipping**: Guest enters shipping address
5. **Payment**: Guest completes Stripe payment
6. **Confirmation**: Order is created with unique lookup token
7. **Order Success**: Guest sees order number and tracking instructions

### Guest Order Tracking Flow

1. Guest visits `/guest-order-lookup/` (or clicks "Track Order" in nav)
2. Enters email address and order number
3. System validates credentials
4. Shows full order details if match found
5. Token stored in session for continued access

### Security Features

- **UUID Tokens**: Each order has unique, unguessable lookup token
- **Email Validation**: Must provide correct email to access order
- **Session Storage**: Token stored in session after successful lookup
- **No Account Linking**: Guest orders remain separate from user accounts

## Testing Checklist

### Guest Checkout Test
- [ ] Add items to cart as guest (not logged in)
- [ ] Click "Proceed to Checkout"
- [ ] Verify email field appears
- [ ] Enter email, shipping address
- [ ] Complete payment (use Stripe test card: 4242 4242 4242 4242)
- [ ] Verify redirect to order success page
- [ ] Verify guest information box appears
- [ ] Check that confirmation email is sent

### Guest Order Lookup Test
- [ ] Navigate to /guest-order-lookup/ or click "Track Order"
- [ ] Enter incorrect email/order number - verify error
- [ ] Enter correct credentials - verify order displays
- [ ] Verify all order information is visible
- [ ] Click "Track Another Order" - verify returns to form

### Registered User Test
- [ ] Verify logged-in users still see "My Orders" link
- [ ] Verify registered checkout still works
- [ ] Verify users cannot see guest orders from other emails

## Admin Panel Updates

Guest orders will appear in the Django admin with:
- Customer shown as "Guest (email@example.com)"
- Order shown as "Order #123 - Guest (email@example.com)"

## Email Notifications

The existing email system (`shop/emails.py`) will work for both:
- **Registered Users**: Email sent to `user.email`
- **Guest Users**: Email sent to `order.guest_email`

## Future Enhancements (Optional)

Consider implementing:
1. **Guest-to-Account Conversion**: Offer account creation after successful guest order
2. **Guest Order History**: Allow guests to see all orders by email (with verification)
3. **Email Marketing**: Capture guest emails for marketing campaigns
4. **SMS Notifications**: Add phone number field for order updates
5. **Social Checkout**: Allow checkout via Google/Facebook accounts

## Stripe Metadata

Guest orders include the following metadata in Stripe PaymentIntent:
- `session_key`: Session identifier
- For authenticated users: `user_id`, `customer_id`

## Troubleshooting

### Migration Issues
If you encounter migration conflicts:
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

### Guest Orders Not Appearing
- Verify `guest_email` field is populated in Order model
- Check that email is being captured from checkout form
- Ensure JavaScript is passing `guest_email` to `process_payment` endpoint

### Order Lookup Not Working
- Verify exact match on email (case-sensitive)
- Confirm order ID is integer, not string with hash
- Check that `order_lookup_token` is being generated

## API Changes Summary

### Modified Endpoints
- `GET/POST /checkout/`: Now accessible without authentication
- `POST /process-payment/`: Accepts `guest_email` parameter

### Response Changes
**process_payment** returns:
```json
{
  "success": true,
  "order_id": 123,
  "order_token": "uuid-string",
  "is_guest": true,
  "message": "Order #123 placed successfully!"
}
```

## Rollback Instructions

If you need to revert these changes:

1. Remove guest checkout views and templates
2. Restore `@login_required` decorators on `checkout()` and `process_payment()`
3. Create migration to make `Customer.user` required again
4. Remove `guest_email` and `order_lookup_token` fields

## Support

For questions or issues with the guest checkout implementation:
- Check Django logs for detailed error messages
- Review Stripe dashboard for payment issues
- Verify email service is configured correctly for guest confirmations

---

**Implementation Date**: 2025
**Django Version**: 5.2
**Stripe Version**: 7.0.0
