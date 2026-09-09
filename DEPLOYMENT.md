# Render deployment and launch review

Render is the selected host. The repository is `https://github.com/dmero/tshirt-web`; the improvements are local and have not been pushed or deployed. No paid infrastructure has been created.

## What is prepared

- `render.yaml`: Python web service (`0.5c-512mb`), PostgreSQL (`0.1c-256mb`), static asset collection and pre-deploy migrations. These are paid plans; review the current price in Render before creating them. PostgreSQL public inbound access is disabled.
- Environment-driven production settings, HTTPS redirects, secure cookies, HSTS, explicit hostnames, WhiteNoise static assets, and S3 product-image storage with signed URLs.
- `Dockerfile`: optional AWS/container fallback. Docker was not running locally, so the container has not been built or tested.
- `requirements-mysql.txt`: preserves a path for using the existing MySQL database. The normal Render installation uses PostgreSQL.

## Local preview

The preview uses `preview.sqlite3`, existing local product images, sample product rows, disabled payments and in-memory email. It does not use the original database or send mail.

```powershell
.venv/Scripts/python manage.py migrate --settings=tshirt_shop.preview_settings
.venv/Scripts/python manage.py createsampledata --settings=tshirt_shop.preview_settings
.venv/Scripts/python manage.py runserver 127.0.0.1:8000 --settings=tshirt_shop.preview_settings
.venv/Scripts/python manage.py test shop --settings=tshirt_shop.preview_settings
```

Never use `preview_settings` as a hosting configuration. For normal local MySQL development, explicitly set `DEBUG=True` and install `requirements-mysql.txt`.

## Deployment steps

1. Create your Render account and connect the GitHub repository. Review and commit the local changes before pushing the selected branch. Do not include `.env`, database exports, payment-test scripts, or local source dumps. Existing `.pyc` files are already tracked in this repository; remove those from Git as a separate repository cleanup.
2. In Render, create a Blueprint from this repository's `render.yaml`. Review the web-service and database charges before confirming creation. Use the same region for the service and database.
3. Set `SITE_URL` and `CSRF_TRUSTED_ORIGINS` to the full HTTPS service URL. Render's assigned hostname is added to `ALLOWED_HOSTS` automatically. For a custom domain, also set `ALLOWED_HOSTS` to its exact hostname(s). The generated secret must have at least 50 characters. Set `TRUST_PROXY=True` only behind Render's trusted HTTPS proxy.
4. Set the Stripe test public, secret, and webhook keys in Render's environment settings. Configure the webhook endpoint as `https://YOUR-HOST/webhook/stripe/` and subscribe to `payment_intent.succeeded`. Test keys and live keys must not be mixed. Do not paste secrets into source code or chat.
5. Configure SMTP credentials, a verified `DEFAULT_FROM_EMAIL`, port and TLS settings. Send a real test email and verify guest links use the hosted domain.
6. For Render image storage, attach a persistent disk at `/var/data`, starting with 1 GB. Set `MEDIA_ROOT=/var/data/media` and `SERVE_PRODUCT_IMAGES=True` on the web service, and leave `AWS_STORAGE_BUCKET_NAME` unset. The app serves catalog JPEG, PNG, WebP and GIF images from this disk with DEBUG=False. Only files referenced by products are served; directory traversal and non-image files are rejected. Existing local images must be copied to `/var/data/media/products/` with their matching database paths. Upload a product image in the admin and check that it still loads after a redeploy. Disk-backed services have brief deploy downtime and cannot scale to multiple instances. Database storage is separate. The `render.yaml` blueprint retains the optional S3 setup; these disk instructions apply to the manually configured service.

   Alternative: create a private S3 bucket and set `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`, `AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY` with bucket-scoped credentials. Leave `SERVE_PRODUCT_IMAGES=False` for S3. The app uses signed S3 URLs.
7. Back up the existing MySQL database before migrating data. A new Render database starts empty: migrations create tables, not your products, users, or orders. Rehearse a Django data export/import to a staging PostgreSQL database, excluding content types/permissions as appropriate. Verify counts, totals, image keys, users, and guest tracking before switching traffic. Do not load preview/sample orders into production. Migration 0005 rejects duplicate nonempty Stripe payment IDs so they can be reconciled without deleting order history.
8. Run `python manage.py check --deploy` with the production environment and create your administrator through Render's shell. Confirm static assets and admin media uploads survive a redeploy.
9. In staging, exercise real Stripe test-mode success, decline, authentication, a closed browser after payment, webhook retries, and refund. Confirm mail delivery and PostgreSQL concurrency behavior. Only enable live payments after these checks and the business details below are complete.

## Payment behavior and operational limits

Orders and line-item prices are saved before the browser confirms payment. Browser confirmation and signed webhooks share idempotent completion, verify the received amount/currency, and decrease stock once. A payment cannot be applied to another session's order. GET requests cannot execute refunds.

Stock is validated before payment but not reserved. If concurrent checkouts exhaust inventory, the paid order is retained as **payment completed / order pending** for staff resolution; stock never goes negative. Staff must review and fulfill or refund these orders. A reservation/expiry workflow is recommended before higher-volume sales. Refunded items are not automatically restocked because physical return condition must be reviewed.

Email failures are logged; there is no durable email retry queue. Add monitoring/reconciliation for paid pending orders, webhook failures, and undelivered email. Guest lookup currently uses order number plus email; add shared-store throttling or email-link verification before a broad public launch. Product deletion still follows the original model's cascade rules, so deactivate products instead of deleting items with order history.

## Business decisions required before live sales

- Confirm shipping destinations, rates, dispatch estimates, returns/refund rules, support contact, and privacy/terms pages. Current checkout charges the product subtotal and displays free shipping; it does not calculate shipping fees or sales tax.
- Confirm product materials, measurements and photography. Generic organic-cotton and fit claims were removed from the detail page; inventory descriptions must still be verified by the owner.
- Confirm a monthly hosting budget and backup/restore process. Render web/database plans and S3 incur separate charges.

## Validation

25 Django regression tests passed on isolated SQLite, including invalid cart inputs, cross-session access, amount/currency checks, duplicate payment/webhook completion, guest emails, and refund GET safety. Production `check --deploy` passed and `collectstatic` completed. Browser review covers the catalog, search, product selection, bag quantities and checkout-unavailable behavior, including a 390px mobile layout and mobile navigation. PostgreSQL concurrency, real Stripe, SMTP, S3 and the deployed environment require staging credentials and remain unverified.

References: [Render Django deployment](https://render.com/docs/deploy-django), [Render Blueprint specification](https://render.com/docs/blueprint-spec), [Stripe payment status and webhooks](https://docs.stripe.com/payments/payment-intents/verifying-status).
