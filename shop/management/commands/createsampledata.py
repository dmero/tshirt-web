from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product, Customer
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample data for the t-shirt shop'
    
    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            {'name': 'Casual', 'slug': 'casual', 'description': 'Comfortable everyday t-shirts'},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Athletic and sports-themed t-shirts'},
            {'name': 'Graphic', 'slug': 'graphic', 'description': 'T-shirts with creative graphics and designs'},
            {'name': 'Vintage', 'slug': 'vintage', 'description': 'Retro and vintage-style t-shirts'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products
        products_data = [
            {
                'name': 'Classic Cotton Tee',
                'slug': 'classic-cotton-tee',
                'description': 'Ultra-soft 100% cotton t-shirt perfect for everyday wear.',
                'price': Decimal('24.99'),
                'category': 'casual',
                'stock': 50,
                'available_sizes': 'XS,S,M,L,XL,XXL',
                'image': 'products/classic-cotton-tee.svg'
            },
            {
                'name': 'Athletic Performance Shirt',
                'slug': 'athletic-performance-shirt',
                'description': 'Moisture-wicking performance tee ideal for workouts and sports.',
                'price': Decimal('34.99'),
                'category': 'sports',
                'stock': 30,
                'available_sizes': 'S,M,L,XL,XXL',
                'image': 'products/athletic-performance-shirt.svg'
            },
            {
                'name': 'Retro Gaming Tee',
                'slug': 'retro-gaming-tee',
                'description': 'Cool vintage gaming graphics on premium cotton blend.',
                'price': Decimal('29.99'),
                'category': 'graphic',
                'stock': 25,
                'available_sizes': 'XS,S,M,L,XL',
                'image': 'products/retro-gaming-tee.svg'
            },
            {
                'name': 'Classic Band Tee',
                'slug': 'classic-band-tee',
                'description': 'Vintage-inspired band t-shirt with distressed graphics.',
                'price': Decimal('32.99'),
                'category': 'vintage',
                'stock': 20,
                'available_sizes': 'S,M,L,XL',
                'image': 'products/classic-band-tee.svg'
            },
            {
                'name': 'Organic Cotton Basic',
                'slug': 'organic-cotton-basic',
                'description': 'Eco-friendly organic cotton t-shirt in various colors.',
                'price': Decimal('27.99'),
                'category': 'casual',
                'stock': 40,
                'available_sizes': 'XS,S,M,L,XL,XXL',
                'image': 'products/organic-cotton-basic.svg'
            },
            {
                'name': 'Fitness Motivation Tee',
                'slug': 'fitness-motivation-tee',
                'description': 'Inspirational fitness quotes on high-performance fabric.',
                'price': Decimal('31.99'),
                'category': 'sports',
                'stock': 35,
                'available_sizes': 'S,M,L,XL,XXL',
                'image': 'products/fitness-motivation-tee.svg'
            }
        ]
        
        for prod_data in products_data:
            category = Category.objects.get(slug=prod_data['category'])
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'name': prod_data['name'],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'category': category,
                    'stock': prod_data['stock'],
                    'available_sizes': prod_data['available_sizes'],
                    'image': prod_data['image'],
                    'active': True
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
