from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = 'Update existing products with image paths'
    
    def handle(self, *args, **options):
        # Map product slugs to image paths
        image_mappings = {
            'classic-cotton-tee': 'products/classic-cotton-tee.svg',
            'athletic-performance-shirt': 'products/athletic-performance-shirt.svg',
            'retro-gaming-tee': 'products/retro-gaming-tee.svg',
            'classic-band-tee': 'products/classic-band-tee.svg',
            'organic-cotton-basic': 'products/organic-cotton-basic.svg',
            'fitness-motivation-tee': 'products/fitness-motivation-tee.svg',
        }
        
        updated_count = 0
        
        for slug, image_path in image_mappings.items():
            try:
                product = Product.objects.get(slug=slug)
                product.image = image_path
                product.save()
                self.stdout.write(f'✓ Updated {product.name} with image: {image_path}')
                updated_count += 1
            except Product.DoesNotExist:
                self.stdout.write(f'✗ Product with slug "{slug}" not found')
        
        self.stdout.write(self.style.SUCCESS(f'\nUpdated {updated_count} products with images!'))
        self.stdout.write('Run "python manage.py checkdata" to verify the changes.')