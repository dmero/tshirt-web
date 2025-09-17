# T-Shirt Shop

Modern Django storefront for browsing t-shirts, managing a cart, and checking out with session-based orders. Includes customer accounts, password resets, and a lightweight admin backend.

## Features
- Catalog browsing with product detail pages and category metadata.
- Client-side cart sidebar syncing with Django JSON endpoints.
- Checkout flow that persists orders and order items for logged-in customers.
- Account management, including signup with email capture and password reset support.
- Seed scripts for demo data and maintenance commands (`createsampledata`, `checkdata`, `createtestorder`, `updateimages`).

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
| `EMAIL_HOST_USER` | From address for emails (e.g., Gmail account) |
| `EMAIL_HOST_PASSWORD` | SMTP/app password |
| `EMAIL_HOST`/`EMAIL_PORT` | SMTP host/port (defaults to Gmail TLS) |
| `DEFAULT_FROM_EMAIL` | Sender shown in password reset emails |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | Toggle TLS/SSL (TLS default) |

MySQL credentials are currently hard-coded in `tshirt_shop/settings.py`; move them into `.env` before deploying.

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

## Email & Password Resets
- Password reset emails use the plain-text template `shop/templates/registration/password_reset_email.txt`.
- SMTP settings come from environment variables (`EMAIL_*`).
- Ensure each user’s `email` field is populated—`SignUpForm` now collects and validates emails for new accounts. For existing users, add emails via the admin site.

## Management Commands
- `createsampledata`: Seeds categories and products.
- `checkdata`: Prints out catalog info for debugging.
- `createtestorder`: Generates a sample order for the authenticated user.
- `updateimages`: Utility for refreshing product images (see script for details).

Run any command with:

```bash
python manage.py <command>
```

## Testing

`shop/tests.py` is currently empty; add coverage for cart operations, order creation, and forms as you evolve the project. Execute with:

```bash
python manage.py test
```

## Deployment Notes
- Turn off `DEBUG` and replace `SECRET_KEY` & database credentials with secure values in production.
- Use `collectstatic` to gather assets if serving via a CDN or reverse proxy.
- Configure a production-ready email provider and domain.

## Contributing
1. Fork and create a feature branch (`git checkout -b feature/my-feature`).
2. Make changes, add tests where possible, and ensure lint/test suites are green.
3. Submit a pull request with a clear summary of the change.

## License

Include licensing information here if applicable.
