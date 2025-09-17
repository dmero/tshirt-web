from django.core.management.base import BaseCommand
from shop.models import Category, Product

class Command(BaseCommand):
    help = 'Check what data exists in the database'
    
    def handle(self, *args, **options):
        self.stdout.write("=== DATABASE CONTENTS ===")
        
        # Check categories
        categories = Category.objects.all()
        self.stdout.write(f"\nCategories ({categories.count()}):")
        for cat in categories:
            self.stdout.write(f"  - {cat.name} (slug: {cat.slug})")
        
        # Check products
        products = Product.objects.all()
        self.stdout.write(f"\nProducts ({products.count()}):")
        for product in products:
            image_status = "✓ Has image" if product.image else "✗ No image"
            self.stdout.write(f"  - {product.name}")
            self.stdout.write(f"    Price: ${product.price}")
            self.stdout.write(f"    Category: {product.category.name}")
            self.stdout.write(f"    Image: {image_status}")
            if product.image:
                self.stdout.write(f"    Image path: {product.image}")
            self.stdout.write(f"    Active: {product.active}")
            self.stdout.write("")
        
        if products.count() == 0:
            self.stdout.write(self.style.WARNING("No products found! Run 'python manage.py createsampledata' to create sample products."))
        
        self.stdout.write("=== END DATABASE CONTENTS ===")