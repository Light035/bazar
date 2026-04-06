import random
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductImage
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(email__in=['buyer@test.com', 'seller@test.com']).delete()

        # Create categories
        self.stdout.write('Creating categories...')
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'slug': 'books', 'description': 'Books and literature'},
            {'name': 'Home & Garden', 'slug': 'home-garden', 'description': 'Home improvement and gardening'},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Sports equipment and accessories'},
        ]

        categories = []
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories.append(category)
            self.stdout.write(f'  + Created category: {category.name}')

        # Create test users
        self.stdout.write('\nCreating test users...')

        buyer = User.objects.create_user(
            email='buyer@test.com',
            password='Test1234!',
            first_name='Test',
            last_name='Buyer',
            email_verified=True
        )
        self.stdout.write(f'  + Created buyer: {buyer.email}')

        seller = User.objects.create_user(
            email='seller@test.com',
            password='Test1234!',
            first_name='Test',
            last_name='Seller',
            is_seller=True,
            email_verified=True
        )
        self.stdout.write(f'  + Created seller: {seller.email}')

        # Create products
        self.stdout.write('\nCreating products...')

        products_data = [
            # Electronics
            {'title': 'Wireless Bluetooth Headphones', 'category': 'Electronics', 'price': 15000, 'description': 'High-quality wireless headphones with noise cancellation'},
            {'title': 'Smart Watch Pro', 'category': 'Electronics', 'price': 35000, 'description': 'Advanced smartwatch with fitness tracking and notifications'},
            {'title': 'USB-C Fast Charger', 'category': 'Electronics', 'price': 3500, 'description': '65W fast charging adapter with multiple ports'},
            {'title': 'Portable Power Bank 20000mAh', 'category': 'Electronics', 'price': 8000, 'description': 'High-capacity power bank for all your devices'},

            # Clothing
            {'title': 'Cotton T-Shirt Pack (3pcs)', 'category': 'Clothing', 'price': 5000, 'description': 'Comfortable cotton t-shirts in various colors'},
            {'title': 'Denim Jeans Classic Fit', 'category': 'Clothing', 'price': 12000, 'description': 'Durable denim jeans with classic fit'},
            {'title': 'Winter Jacket Waterproof', 'category': 'Clothing', 'price': 25000, 'description': 'Warm waterproof jacket for cold weather'},
            {'title': 'Running Shoes Sport', 'category': 'Clothing', 'price': 18000, 'description': 'Lightweight running shoes with cushioned sole'},

            # Books
            {'title': 'Python Programming Guide', 'category': 'Books', 'price': 4500, 'description': 'Complete guide to Python programming for beginners'},
            {'title': 'Business Strategy Handbook', 'category': 'Books', 'price': 6000, 'description': 'Essential strategies for modern business success'},
            {'title': 'Cooking Masterclass Book', 'category': 'Books', 'price': 3500, 'description': 'Learn professional cooking techniques at home'},
            {'title': 'World History Encyclopedia', 'category': 'Books', 'price': 8500, 'description': 'Comprehensive world history reference book'},

            # Home & Garden
            {'title': 'LED Desk Lamp Adjustable', 'category': 'Home & Garden', 'price': 7000, 'description': 'Modern LED desk lamp with adjustable brightness'},
            {'title': 'Garden Tool Set 10pcs', 'category': 'Home & Garden', 'price': 9500, 'description': 'Complete gardening tool set for home use'},
            {'title': 'Kitchen Knife Set Professional', 'category': 'Home & Garden', 'price': 15000, 'description': 'Professional chef knife set with storage block'},
            {'title': 'Vacuum Cleaner Cordless', 'category': 'Home & Garden', 'price': 28000, 'description': 'Powerful cordless vacuum cleaner for home'},

            # Sports
            {'title': 'Yoga Mat Premium', 'category': 'Sports', 'price': 4000, 'description': 'Non-slip yoga mat with carrying strap'},
            {'title': 'Dumbbell Set 20kg', 'category': 'Sports', 'price': 12000, 'description': 'Adjustable dumbbell set for home workouts'},
            {'title': 'Tennis Racket Professional', 'category': 'Sports', 'price': 22000, 'description': 'Professional tennis racket with carbon frame'},
            {'title': 'Football Official Size', 'category': 'Sports', 'price': 5500, 'description': 'Official size football for training and matches'},
        ]

        products_created = 0
        images_created = 0

        for prod_data in products_data:
            category_name = prod_data.pop('category')
            # Fetch category from database to ensure we have the correct ID
            category = Category.objects.get(name=category_name)

            product = Product.objects.create(
                title=prod_data['title'],
                slug=prod_data['title'].lower().replace(' ', '-'),
                description=prod_data['description'],
                price=Decimal(prod_data['price']),
                category=category,
                seller=seller,
                stock=random.randint(5, 100),
                is_active=True
            )
            products_created += 1
            self.stdout.write(f'  + Created product: {product.title} ({product.price} T)')

            # Add 2-3 images for each product
            num_images = random.randint(2, 3)
            seed = product.slug

            for i in range(num_images):
                try:
                    # Generate unique seed for each image
                    image_seed = f"{seed}-{i}"
                    image_url = f"https://picsum.photos/seed/{image_seed}/800/600"

                    # Download image
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        # Create ProductImage
                        img_content = ContentFile(response.content)
                        product_image = ProductImage.objects.create(
                            product=product,
                            is_main=(i == 0),  # First image is main
                            order=i
                        )
                        product_image.image.save(f"{product.slug}-{i}.jpg", img_content, save=True)
                        images_created += 1

                        if i == 0:
                            self.stdout.write(f'    + Added {num_images} images (main: {image_seed})')
                except Exception as e:
                    self.stdout.write(f'    ! Failed to add image: {str(e)}')

        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('DATABASE POPULATION COMPLETE!'))
        self.stdout.write('='*60)
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  - Categories: {len(categories)}')
        self.stdout.write(f'  - Products: {products_created}')
        self.stdout.write(f'  - Images: {images_created}')
        self.stdout.write(f'  - Users: 2')
        self.stdout.write(f'\nTest Accounts:')
        self.stdout.write(f'  - Buyer: buyer@test.com / Test1234!')
        self.stdout.write(f'  - Seller: seller@test.com / Test1234!')
        self.stdout.write('\n' + '='*60)
