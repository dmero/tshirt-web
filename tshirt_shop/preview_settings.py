"""Isolated local preview/test configuration; never use for deployment."""
import os
os.environ['DEBUG'] = 'True'
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
from .settings import *  # noqa: F403
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'preview.sqlite3'}}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
STRIPE_PUBLIC_KEY = ''
STRIPE_SECRET_KEY = ''
STRIPE_WEBHOOK_SECRET = ''
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
