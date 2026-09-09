from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase, RequestFactory, override_settings
from django.http import Http404
from PIL import Image

from .media import product_image
from .models import Category, Product


class ProductImageTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'products').mkdir()
        self.settings_override = override_settings(MEDIA_ROOT=self.root, SERVE_PRODUCT_IMAGES=True, DEBUG=False)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.request = RequestFactory().get('/media/products/tee.png')
        category = Category.objects.create(name='Tees', slug='tees')
        self.product = Product.objects.create(name='Tee', slug='tee', price=10, category=category, image='products/tee.png')
        Image.new('RGB', (2, 2)).save(self.root / 'products' / 'tee.png')

    def test_serves_image_with_production_settings(self):
        response = product_image(self.request, 'tee.png')
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(b''.join(response.streaming_content), (self.root / 'products' / 'tee.png').read_bytes())
        response.close()

    def test_rejects_missing_unlisted_and_traversal_paths(self):
        for filename in ('missing.png', '../private.txt', '../../private.txt'):
            with self.subTest(filename=filename), self.assertRaises(Http404):
                product_image(self.request, filename)

    def test_rejects_html_disguised_as_image(self):
        (self.root / 'products' / 'tee.png').write_text('<script>alert(1)</script>')
        with self.assertRaises(Http404):
            product_image(self.request, 'tee.png')

    @override_settings(SERVE_PRODUCT_IMAGES=False)
    def test_disk_serving_is_opt_in(self):
        with self.assertRaises(Http404):
            product_image(self.request, 'tee.png')
