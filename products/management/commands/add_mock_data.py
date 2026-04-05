from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductImage
from decimal import Decimal


class Command(BaseCommand):
    help = 'Add mock data for categories and products'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating mock data...')

        # Create Categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'description': 'Books and literature'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
            {'name': 'Sports', 'description': 'Sports equipment and accessories'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create Products
        products_data = [
            # Electronics
            {'title': 'Wireless Headphones', 'description': 'High-quality wireless headphones with noise cancellation', 'price': '99.99', 'stock': 50, 'category': 'Electronics'},
            {'title': 'Smartphone', 'description': 'Latest model smartphone with advanced features', 'price': '699.99', 'stock': 30, 'category': 'Electronics'},
            {'title': 'Laptop', 'description': 'Powerful laptop for work and gaming', 'price': '1299.99', 'stock': 20, 'category': 'Electronics'},
            {'title': 'Smart Watch', 'description': 'Fitness tracking smartwatch', 'price': '249.99', 'stock': 40, 'category': 'Electronics'},

            # Clothing
            {'title': 'Cotton T-Shirt', 'description': 'Comfortable cotton t-shirt in various colors', 'price': '19.99', 'stock': 100, 'category': 'Clothing'},
            {'title': 'Jeans', 'description': 'Classic blue denim jeans', 'price': '49.99', 'stock': 75, 'category': 'Clothing'},
            {'title': 'Winter Jacket', 'description': 'Warm winter jacket with hood', 'price': '89.99', 'stock': 45, 'category': 'Clothing'},
            {'title': 'Running Shoes', 'description': 'Lightweight running shoes', 'price': '79.99', 'stock': 60, 'category': 'Clothing'},

            # Books
            {'title': 'Python Programming', 'description': 'Complete guide to Python programming', 'price': '39.99', 'stock': 80, 'category': 'Books'},
            {'title': 'Science Fiction Novel', 'description': 'Bestselling sci-fi adventure', 'price': '14.99', 'stock': 120, 'category': 'Books'},
            {'title': 'Cooking Masterclass', 'description': 'Professional cooking techniques', 'price': '29.99', 'stock': 55, 'category': 'Books'},

            # Home & Garden
            {'title': 'Coffee Maker', 'description': 'Automatic coffee maker with timer', 'price': '59.99', 'stock': 35, 'category': 'Home & Garden'},
            {'title': 'Garden Tools Set', 'description': 'Complete set of garden tools', 'price': '44.99', 'stock': 25, 'category': 'Home & Garden'},
            {'title': 'LED Desk Lamp', 'description': 'Adjustable LED desk lamp', 'price': '34.99', 'stock': 70, 'category': 'Home & Garden'},

            # Sports
            {'title': 'Yoga Mat', 'description': 'Non-slip yoga mat with carrying strap', 'price': '24.99', 'stock': 90, 'category': 'Sports'},
            {'title': 'Dumbbell Set', 'description': 'Adjustable dumbbell set', 'price': '149.99', 'stock': 30, 'category': 'Sports'},
            {'title': 'Tennis Racket', 'description': 'Professional tennis racket', 'price': '89.99', 'stock': 40, 'category': 'Sports'},
        ]

        for prod_data in products_data:
            category = categories[prod_data['category']]
            product, created = Product.objects.get_or_create(
                title=prod_data['title'],
                defaults={
                    'description': prod_data['description'],
                    'price': Decimal(prod_data['price']),
                    'stock': prod_data['stock'],
                    'category': category,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.title}'))

        self.stdout.write(self.style.SUCCESS('Mock data created successfully!'))
