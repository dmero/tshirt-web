# T-Shirt Shop 🛍️

Modern Django e-commerce platform for browsing t-shirts, managing cart, and secure checkout with **Stripe payment processing**. Full-featured with automated email notifications, order tracking, refund management, and professional admin interface.

## ✨ Features

### 🛒 **Shopping Experience**
- Catalog browsing with product detail pages and category filtering
- Real-time cart sidebar syncing with Django JSON endpoints
- Session-based cart management
- Responsive design with modern UI

### 💳 **Payment & Checkout**
- **Stripe Integration** - Secure credit card processing
- PCI-DSS compliant (Stripe Elements)
- Test and live payment modes
- PaymentIntent tracking
- Automatic order creation on successful payment

### 📧 **Email Notifications**
- **Order Confirmation** - Sent immediately after payment
- **Shipped Notification** - Includes tracking number and carrier link
- **Delivered Notification** - Delivery confirmation with feedback request
- **Refund Confirmation** - Automatic email when refund processed
- Beautiful HTML and plain-text email templates

### 📦 **Shipping & Tracking**
- Tracking number and URL management
- Automatic email notifications on status changes (Django Signals)
- Customer tracking display in "My Orders" page
- Bulk admin actions (Mark as Shipped/Delivered)

### 💰 **Refund System**
- Stripe refund integration
- Admin bulk refund actions
- Automatic refund emails
- Full refund history tracking

### 👤 **Customer Management**
- User registration with email validation
- Customer profiles with order history
- Password reset functionality
- "My Orders" page with tracking information

### 🎛️ **Admin Interface**
- Enhanced order management with customer names
- Inline order display in customer profiles
- Bulk actions for shipping and refunds
- Searchable orders by tracking number, customer, email
- Organized fieldsets for better UX

## Stack
- Python 3.11+
- Django 5.2
- MySQL 8 (configured via `django.db.backends.mysql`)
- Front-end assets in `static/` (vanilla JS + CSS)

## Getting Started

### 1. Clone and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # create this from your current environment if missing
```

> **Note:** If `requirements.txt` is not yet generated, create one with `pip freeze > requirements.txt` once dependencies are installed.

### 2. Configure environment variables

Sensitive settings (database credentials, SMTP, etc.) are loaded from `.env`. Copy the template and fill in real values:

```bash
cp .env.example .env
# edit .env to set MySQL and SMTP credentials
```

Required keys:

| Variable | Description |
| --- | --- |
| `STRIPE_PUBLIC_KEY` | Stripe publishable key (pk_test_* for testing) |
| `STRIPE_SECRET_KEY` | Stripe secret key (sk_test_* for testing) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (optional) |
| `EMAIL_HOST_USER` | From address for emails (e.g., Gmail account) |
| `EMAIL_HOST_PASSWORD` | SMTP/app password |
| `EMAIL_HOST`/`EMAIL_PORT` | SMTP host/port (defaults to Gmail TLS) |
| `DEFAULT_FROM_EMAIL` | Sender shown in emails |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | Toggle TLS/SSL (TLS default) |

**Important:** Never commit your `.env` file! It contains sensitive API keys and passwords.

### 3. Database setup

Create the MySQL database and user referenced in `settings.py`, then run migrations:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Optionally seed demo data:

```bash
python manage.py createsampledata
```

### 4. Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to browse the storefront. Admin UI is available at `/admin/`.

## 📚 Documentation

Comprehensive guides are available in the project root:

- **[STRIPE_SETUP.md](STRIPE_SETUP.md)** - Complete Stripe integration guide
  - Installation and configuration
  - Test card numbers
  - Webhook setup
  - Troubleshooting

- **[EMAIL_AND_REFUND_GUIDE.md](EMAIL_AND_REFUND_GUIDE.md)** - Email system and refunds
  - Email template customization
  - Refund processing
  - Gmail configuration
  - Testing procedures

- **[SHIPPING_NOTIFICATIONS_GUIDE.md](SHIPPING_NOTIFICATIONS_GUIDE.md)** - Shipping emails
  - Shipped notification setup
  - Delivered notification setup
  - Django Signals configuration
  - Admin bulk actions

- **[MY_ORDERS_TRACKING_GUIDE.md](MY_ORDERS_TRACKING_GUIDE.md)** - Customer tracking
  - Tracking display setup
  - UI customization
  - Carrier integration
  - Mobile responsiveness

## 📧 Email & Password Resets
- Automated emails for orders, shipping, delivery, and refunds
- Password reset emails use the template `shop/templates/registration/password_reset_email.txt`
- SMTP settings come from environment variables (`EMAIL_*`)
- All email templates available in `shop/templates/shop/emails/`

## Management Commands
- `createsampledata`: Seeds categories and products.
- `checkdata`: Prints out catalog info for debugging.
- `createtestorder`: Generates a sample order for the authenticated user.

Run any command with:

```bash
python manage.py <command>
```

## Testing

`shop/tests.py` is currently empty; add coverage for cart operations, order creation, and forms as you evolve the project. Execute with:

```bash
python manage.py test
```

## 🚀 Deployment Notes

### **Production Checklist:**

**Security:**
- ✅ Turn off `DEBUG = False`
- ✅ Replace `SECRET_KEY` with secure value
- ✅ Update `ALLOWED_HOSTS`
- ✅ Enable HTTPS

**Stripe:**
- ✅ Switch to live Stripe keys (`pk_live_*` and `sk_live_*`)
- ✅ Set up production webhooks
- ✅ Test with real (small) transactions

**Email:**
- ✅ Use production email service (SendGrid, Mailgun, AWS SES)
- ✅ Configure SPF, DKIM, DMARC records
- ✅ Test email deliverability

**Database:**
- ✅ Use production database (not SQLite)
- ✅ Secure credentials in environment variables
- ✅ Set up regular backups

**Static Files:**
- ✅ Run `python manage.py collectstatic`
- ✅ Serve via CDN or reverse proxy (nginx/Apache)

**Monitoring:**
- ✅ Set up error logging (Sentry, etc.)
- ✅ Monitor payment success rates
- ✅ Track email delivery

## Contributing
1. Fork and create a feature branch (`git checkout -b feature/my-feature`).
2. Make changes, add tests where possible, and ensure lint/test suites are green.
3. Submit a pull request with a clear summary of the change.

## License

Include licensing information here if applicable.
