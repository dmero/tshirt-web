from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.http import require_safe
from PIL import Image, UnidentifiedImageError

from .models import Product


@require_safe
def product_image(request, filename):
    """Serve only catalog raster images from the explicitly enabled local disk."""
    if not settings.SERVE_PRODUCT_IMAGES:
        raise Http404
    root = Path(settings.MEDIA_ROOT).resolve()
    target = (root / 'products' / filename).resolve()
    if not target.is_relative_to(root / 'products'):
        raise Http404
    if not Product.objects.filter(image='products/' + filename).exists():
        raise Http404
    stream = None
    try:
        stream = target.open('rb')
        with Image.open(target) as uploaded:
            content_type = {'JPEG': 'image/jpeg', 'PNG': 'image/png',
                            'WEBP': 'image/webp', 'GIF': 'image/gif'}.get(uploaded.format)
        if not content_type:
            raise Http404
        response = FileResponse(stream, content_type=content_type)
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'public, max-age=300'
        return response
    except (OSError, UnidentifiedImageError, Http404):
        if stream is not None:
            stream.close()
        raise Http404
